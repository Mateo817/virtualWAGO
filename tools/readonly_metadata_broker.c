#define _GNU_SOURCE
/*
 * Narrow seccomp user-notification mediator for one read-only metadata file.
 * This process must itself already be inside the intended isolated mount and
 * device namespace. CONTINUE for unrelated opens is safe only under that
 * independently enforced namespace/mount policy.
 */
#include <errno.h>
#include <fcntl.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/magic.h>
#include <linux/seccomp.h>
#include <linux/openat2.h>
#include <poll.h>
#include <signal.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <sys/mount.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/statfs.h>
#include <sys/statvfs.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

#ifdef VIRTUALWAGO_METADATA_TEST_FILE
#define PROTECTED_PATH VIRTUALWAGO_METADATA_TEST_FILE
#define PROTECTED_MAGIC TMPFS_MAGIC
#else
#define PROTECTED_PATH "/dev/eeprom"
#define PROTECTED_MAGIC SYSFS_MAGIC
#endif

#define MAX_TIMEOUT_SECONDS 30
#define NOTIFICATION_POLL_MS 50
#define SIGNAL_GRACE_MS 200

static volatile sig_atomic_t caught_signal;
static bool diagnostics;
static uint64_t notified, continued, protected_opens, mediated, path_errors;
static int last_path_error;
static int64_t operation_deadline = -1;
/* Numeric diagnostics only; no child arguments or metadata contents. */
enum kill_cause {
  KILL_NONE = 0, KILL_SETUP = 1, KILL_WAIT = 2, KILL_CLOCK = 3,
  KILL_GRACE = 4, KILL_CONTROL = 5, KILL_RECV = 6,
  KILL_LISTENER = 7, KILL_CLEANUP = 8, KILL_ATOMIC_GRANT = 9
};
static enum kill_cause kill_reason;
static int last_control_errno;
static int child_signal;
static bool atomic_grant_failed;

static void kill_owned_child(pid_t child, enum kill_cause reason) {
  if (kill_reason == KILL_NONE) kill_reason = reason;
  (void)kill(child, SIGKILL);
}

static void count_event(uint64_t *counter) {
  if (*counter < UINT64_MAX) ++*counter;
}

static void remember_signal(int signal_number) { caught_signal = signal_number; }
static void interrupt_wait(int signal_number) {
  (void)signal_number;
}

static void restore_alarm_state(const struct sigaction *old_action,
                                const struct itimerval *old_timer,
                                const sigset_t *original_mask) {
  sigset_t alarm_set, pending;
  sigemptyset(&alarm_set);
  sigaddset(&alarm_set, SIGALRM);
  (void)sigprocmask(SIG_BLOCK, &alarm_set, NULL);
  struct itimerval disabled = {0};
  (void)setitimer(ITIMER_REAL, &disabled, NULL);
  if (sigpending(&pending) == 0 && sigismember(&pending, SIGALRM) == 1) {
    struct timespec no_wait = {0, 0};
    (void)sigtimedwait(&alarm_set, NULL, &no_wait);
  }
  (void)sigaction(SIGALRM, old_action, NULL);
  (void)setitimer(ITIMER_REAL, old_timer, NULL);
  (void)sigprocmask(SIG_SETMASK, original_mask, NULL);
}

static int64_t monotonic_milliseconds(void) {
  struct timespec now;
  if (clock_gettime(CLOCK_MONOTONIC, &now) != 0 || now.tv_sec < 0) return -1;
  return (int64_t)now.tv_sec * 1000 + (int64_t)now.tv_nsec / 1000000;
}

/* The 100 ms wakeup bounds RECV only: O_NONBLOCK does not bound that ioctl.
 * During reply/atomic ADDFD handling use the global deadline instead. Drain an
 * old pending wakeup while blocked so it cannot interrupt a subsequent grant.
 * A genuinely interrupted ADDFD_SEND remains fail-closed; it is never retried.
 */
static int arm_operation_alarm(unsigned max_wait_ms) {
  sigset_t alarm_set, previous_mask;
  sigemptyset(&alarm_set);
  sigaddset(&alarm_set, SIGALRM);
  if (sigprocmask(SIG_BLOCK, &alarm_set, &previous_mask) != 0) return -1;
  struct itimerval timer = {0};
  int result = setitimer(ITIMER_REAL, &timer, NULL);
  int saved = errno;
  if (result == 0) {
    struct timespec no_wait = {0, 0};
    (void)sigtimedwait(&alarm_set, NULL, &no_wait);
    int64_t now = monotonic_milliseconds();
    int64_t remaining = operation_deadline - now;
    if (now < 0 || operation_deadline < 0 || remaining <= 0) {
      result = -1;
      saved = now < 0 ? EIO : ETIMEDOUT;
    } else {
      if (max_wait_ms != 0u && remaining > (int64_t)max_wait_ms)
        remaining = (int64_t)max_wait_ms;
      timer.it_value.tv_sec = (time_t)(remaining / 1000);
      timer.it_value.tv_usec = (suseconds_t)((remaining % 1000) * 1000);
      result = setitimer(ITIMER_REAL, &timer, NULL);
      saved = errno;
    }
  }
  if (sigprocmask(SIG_SETMASK, &previous_mask, NULL) != 0) {
    result = -1;
    saved = errno;
  }
  errno = saved;
  return result;
}

/* SEND and ID_VALID can only return EINTR before changing notification state
 * (kernel/seccomp.c mutex_lock_interruptible). Bound retries by both attempts
 * and the unchanged global deadline; never use this for ADDFD_FLAG_SEND.
 */
static int retry_control(int listener, unsigned long command, void *argument) {
  for (unsigned attempt = 0; attempt < 64u; ++attempt) {
    int64_t now = monotonic_milliseconds();
    if (now < 0 || now >= operation_deadline || caught_signal != 0) {
      errno = now < 0 ? EIO : caught_signal != 0 ? ECANCELED : ETIMEDOUT;
      last_control_errno = errno;
      return -1;
    }
    int result = ioctl(listener, command, argument);
    if (result >= 0) return result;
    last_control_errno = errno;
    if (errno != EINTR) return -1;
  }
  errno = EINTR;
  return -1;
}

static bool reap_child_bounded(pid_t child, int *status, unsigned timeout_ms) {
  int64_t started = monotonic_milliseconds();
  if (started < 0) return false;
  int64_t deadline = started + (int64_t)timeout_ms;
  for (;;) {
    pid_t result = waitpid(child, status, WNOHANG);
    if (result == child) return true;
    if (result < 0 && errno != EINTR) return false;
    int64_t now = monotonic_milliseconds();
    if (now < 0 || now >= deadline) return false;
    (void)poll(NULL, 0, 10);
  }
}

static int send_listener(int socket_fd, int listener_fd) {
  char marker = 'L';
  struct iovec vector = {.iov_base = &marker, .iov_len = 1};
  char control[CMSG_SPACE(sizeof(int))];
  memset(control, 0, sizeof(control));
  struct msghdr message = {0};
  message.msg_iov = &vector;
  message.msg_iovlen = 1;
  message.msg_control = control;
  message.msg_controllen = sizeof(control);
  struct cmsghdr *header = CMSG_FIRSTHDR(&message);
  header->cmsg_level = SOL_SOCKET;
  header->cmsg_type = SCM_RIGHTS;
  header->cmsg_len = CMSG_LEN(sizeof(int));
  memcpy(CMSG_DATA(header), &listener_fd, sizeof(listener_fd));
  return sendmsg(socket_fd, &message, MSG_NOSIGNAL) == 1 ? 0 : -1;
}

static int receive_listener(int socket_fd) {
  char marker = 0;
  struct iovec vector = {.iov_base = &marker, .iov_len = 1};
  char control[CMSG_SPACE(sizeof(int))];
  memset(control, 0, sizeof(control));
  struct msghdr message = {0};
  message.msg_iov = &vector;
  message.msg_iovlen = 1;
  message.msg_control = control;
  message.msg_controllen = sizeof(control);
  ssize_t received;
  do { received = recvmsg(socket_fd, &message, MSG_CMSG_CLOEXEC); }
  while (received < 0 && errno == EINTR);
  if (received != 1 || marker != 'L' || (message.msg_flags & MSG_CTRUNC) != 0)
    return -1;
  struct cmsghdr *header = CMSG_FIRSTHDR(&message);
  if (header == NULL || header->cmsg_level != SOL_SOCKET ||
      header->cmsg_type != SCM_RIGHTS || header->cmsg_len != CMSG_LEN(sizeof(int)))
    return -1;
  int listener;
  memcpy(&listener, CMSG_DATA(header), sizeof(listener));
  return listener;
}

static int install_open_filter(int control_fd) {
#if defined(__x86_64__)
  const uint32_t expected_arch = AUDIT_ARCH_X86_64;
#elif defined(__aarch64__)
  const uint32_t expected_arch = AUDIT_ARCH_AARCH64;
#elif defined(__arm__)
  const uint32_t expected_arch = AUDIT_ARCH_ARM;
#else
#error "Add an explicit AUDIT_ARCH gate for this target architecture"
#endif
  struct sock_filter instructions[16];
  size_t count = 0;
#define EMIT(code_, jt_, jf_, k_) \
  do { instructions[count++] = (struct sock_filter)BPF_STMT((code_), (k_)); } while (0)
  EMIT(BPF_LD | BPF_W | BPF_ABS, 0, 0, offsetof(struct seccomp_data, arch));
  instructions[count++] = (struct sock_filter)BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K,
                                                        expected_arch, 1, 0);
  EMIT(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_KILL_PROCESS);
  EMIT(BPF_LD | BPF_W | BPF_ABS, 0, 0, offsetof(struct seccomp_data, nr));

  size_t open_comparisons[3];
  size_t open_comparison_count = 0;
#if defined(__NR_open)
  open_comparisons[open_comparison_count] = count;
  instructions[count++] = (struct sock_filter)BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K,
                                                        __NR_open, 0, 0);
  ++open_comparison_count;
#endif
#if defined(__NR_openat)
  open_comparisons[open_comparison_count] = count;
  instructions[count++] = (struct sock_filter)BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K,
                                                        __NR_openat, 0, 0);
  ++open_comparison_count;
#endif
#if defined(__NR_openat2)
  open_comparisons[open_comparison_count] = count;
  instructions[count++] = (struct sock_filter)BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K,
                                                        __NR_openat2, 0, 0);
  ++open_comparison_count;
#endif
  EMIT(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ALLOW);
  size_t notification_index = count;
  EMIT(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_USER_NOTIF);
  for (size_t i = 0; i < open_comparison_count; ++i)
    instructions[open_comparisons[i]].jt =
        (uint8_t)(notification_index - open_comparisons[i] - 1u);
#undef EMIT
  struct sock_fprog program = {.len = (unsigned short)count,
                               .filter = instructions};
  if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) return -1;
  int listener = (int)syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER,
                              SECCOMP_FILTER_FLAG_NEW_LISTENER, &program);
  if (listener < 0) return -1;
  if (send_listener(control_fd, listener) != 0) {
    close(listener);
    return -1;
  }
  close(listener);
  return 0;
}

static int64_t child_arg_path(pid_t child, uintptr_t remote, char *path) {
  if (remote == 0u) return -EFAULT;
  size_t copied = 0;
  while (copied < PATH_MAX) {
    size_t amount = PATH_MAX - copied;
    if (amount > 64u) amount = 64u;
    struct iovec local = {.iov_base = path + copied, .iov_len = amount};
    struct iovec remote_iov = {.iov_base = (void *)(remote + copied),
                               .iov_len = amount};
    ssize_t got = process_vm_readv(child, &local, 1, &remote_iov, 1, 0);
    if (got < 0) return -errno;
    if (got == 0) return -EFAULT;
    void *terminator = memchr(path + copied, '\0', (size_t)got);
    if (terminator != NULL) return (char *)terminator - path + 1;
    copied += (size_t)got;
    if ((size_t)got < amount) return -EFAULT;
  }
  return -ENAMETOOLONG;
}

static bool allowed_original_flags(uint64_t flags) {
  /* Original ARM libc open64 adds O_LARGEFILE. It grants no write access. */
  uint64_t access_and_other = flags & ~((uint64_t)O_CLOEXEC | (uint64_t)O_LARGEFILE);
  return access_and_other == (uint64_t)O_RDONLY ||
         access_and_other == (uint64_t)O_RDWR;
}

static int open_protected_readonly(void) {
  struct stat path_before;
  if (fstatat(AT_FDCWD, PROTECTED_PATH, &path_before,
              AT_SYMLINK_NOFOLLOW) != 0 || !S_ISREG(path_before.st_mode)) {
    errno = EACCES;
    return -1;
  }
  int path_fd = open(PROTECTED_PATH, O_PATH | O_NOFOLLOW | O_CLOEXEC);
  if (path_fd < 0) return -1;
  struct stat pinned;
  struct statfs pinned_fs;
  if (fstat(path_fd, &pinned) != 0 || !S_ISREG(pinned.st_mode) ||
      fstatfs(path_fd, &pinned_fs) != 0 ||
      (unsigned long)pinned_fs.f_type != PROTECTED_MAGIC) {
    close(path_fd);
    errno = EACCES;
    return -1;
  }
  char proc_path[64];
  int length = snprintf(proc_path, sizeof(proc_path), "/proc/self/fd/%d", path_fd);
  if (length <= 0 || (size_t)length >= sizeof(proc_path)) {
    close(path_fd);
    errno = EACCES;
    return -1;
  }
  struct statvfs mount_before;
  if (statvfs(proc_path, &mount_before) != 0 ||
      (mount_before.f_flag & ST_RDONLY) == 0) {
    close(path_fd);
    errno = EACCES;
    return -1;
  }
  int data_fd = open(proc_path, O_RDONLY | O_CLOEXEC);
  if (data_fd < 0) {
    close(path_fd);
    return -1;
  }
  struct stat reopened;
  struct stat path_after;
  struct statfs reopened_fs;
  struct statvfs mount_info;
  bool valid = fstat(data_fd, &reopened) == 0 && S_ISREG(reopened.st_mode) &&
               reopened.st_dev == pinned.st_dev && reopened.st_ino == pinned.st_ino &&
               path_before.st_dev == pinned.st_dev && path_before.st_ino == pinned.st_ino &&
               fstatat(AT_FDCWD, PROTECTED_PATH, &path_after,
                       AT_SYMLINK_NOFOLLOW) == 0 &&
               S_ISREG(path_after.st_mode) && path_after.st_dev == pinned.st_dev &&
               path_after.st_ino == pinned.st_ino &&
               fstatfs(data_fd, &reopened_fs) == 0 &&
               (unsigned long)reopened_fs.f_type == PROTECTED_MAGIC &&
               statvfs(proc_path, &mount_info) == 0 &&
               (mount_info.f_flag & ST_RDONLY) != 0 &&
               (mount_before.f_flag & ST_RDONLY) != 0;
  close(path_fd);
  if (!valid) {
    close(data_fd);
    errno = EACCES;
    return -1;
  }
  return data_fd;
}

static int respond(struct seccomp_notif *request, int listener, int error) {
  struct seccomp_notif_resp response = {.id = request->id,
                                        .error = error == 0 ? 0 : -error,
                                        .val = 0, .flags = 0};
  return retry_control(listener, SECCOMP_IOCTL_NOTIF_SEND, &response);
}

static int request_path_pointer(const struct seccomp_notif *request,
                                uintptr_t *path_ptr) {
#ifdef __NR_open
  if (request->data.nr == __NR_open) {
    *path_ptr = (uintptr_t)request->data.args[0];
    return 0;
  }
#endif
#ifdef __NR_openat
  if (request->data.nr == __NR_openat) {
    *path_ptr = (uintptr_t)request->data.args[1];
    return 0;
  }
#endif
#ifdef __NR_openat2
  if (request->data.nr == __NR_openat2) {
    *path_ptr = (uintptr_t)request->data.args[1];
    return 0;
  }
#endif
  return -ENOSYS;
}

static int request_protected_flags(const struct seccomp_notif *request,
                                   uint64_t *flags) {
#ifdef __NR_open
  if (request->data.nr == __NR_open) {
    *flags = request->data.args[1];
    return 0;
  }
#endif
#ifdef __NR_openat
  if (request->data.nr == __NR_openat) {
    *flags = request->data.args[2];
    return 0;
  }
#endif
#ifdef __NR_openat2
  if (request->data.nr == __NR_openat2) {
    struct open_how how;
    size_t open_how_size = (size_t)request->data.args[3];
    if (open_how_size != sizeof(how)) return -EINVAL;
    struct iovec local = {.iov_base = &how, .iov_len = sizeof(how)};
    struct iovec remote = {.iov_base = (void *)(uintptr_t)request->data.args[2],
                           .iov_len = sizeof(how)};
    if (process_vm_readv((pid_t)request->pid, &local, 1, &remote, 1, 0) != sizeof(how))
      return -EFAULT;
    if (how.mode != 0 || how.resolve != 0) return -EINVAL;
    *flags = how.flags;
    return 0;
  }
#endif
  return -ENOSYS;
}

static int handle_notification(int listener, struct seccomp_notif *request,
                               char *path_buffer) {
  count_event(&notified);
  if (retry_control(listener, SECCOMP_IOCTL_NOTIF_ID_VALID, &request->id) != 0)
    return errno == ENOENT ? 0 : -1;
  uintptr_t path_pointer = 0;
  uint64_t flags = 0;
  int parsed = request_path_pointer(request, &path_pointer);
  if (parsed != 0) return respond(request, listener, -parsed);
  int64_t length = child_arg_path((pid_t)request->pid, path_pointer, path_buffer);
  if (length < 0) {
    count_event(&path_errors);
    last_path_error = (int)-length;
    return respond(request, listener, last_path_error);
  }
  if (strcmp(path_buffer, PROTECTED_PATH) != 0) {
    count_event(&continued);
    struct seccomp_notif_resp response = {.id = request->id, .val = 0,
        .error = 0, .flags = SECCOMP_USER_NOTIF_FLAG_CONTINUE};
    return retry_control(listener, SECCOMP_IOCTL_NOTIF_SEND, &response);
  }
  count_event(&protected_opens);
  parsed = request_protected_flags(request, &flags);
  if (parsed != 0) return respond(request, listener, -parsed);
  if (!allowed_original_flags(flags)) return respond(request, listener, EACCES);
  int data_fd = open_protected_readonly();
  if (data_fd < 0) return respond(request, listener, errno == 0 ? EACCES : errno);
  if (retry_control(listener, SECCOMP_IOCTL_NOTIF_ID_VALID, &request->id) != 0) {
    int saved = errno;
    close(data_fd);
    errno = saved;
    return saved == ENOENT ? 0 : -1;
  }
  struct seccomp_notif_addfd add = {.id = request->id,
      .flags = SECCOMP_ADDFD_FLAG_SEND, .srcfd = (uint32_t)data_fd,
      .newfd = 0, .newfd_flags = (flags & (uint64_t)O_CLOEXEC) != 0u ? O_CLOEXEC : 0};
  int result = ioctl(listener, SECCOMP_IOCTL_NOTIF_ADDFD, &add);
  int saved = errno;
  close(data_fd);
  if (result < 0) {
    /* Never CONTINUE a protected open after any broker-side failure. */
    last_control_errno = saved;
    if (saved == ENOENT) return 0;
    /* An interrupted atomic SEND may already have changed state to REPLIED.
     * Neither a second ADDFD nor a fallback reply is safe in that case. */
    if (saved == EINTR || saved == EINPROGRESS) {
      atomic_grant_failed = true;
      errno = saved;
      return -1;
    }
    return respond(request, listener, EACCES);
  }
  count_event(&mediated);
  return 0; /* ADDFD_FLAG_SEND returned the descriptor atomically. */
}

static int child_exec(int control_fd, char **command, pid_t expected_parent) {
  if (prctl(PR_SET_PDEATHSIG, SIGKILL) != 0 || getppid() != expected_parent)
    _exit(125);
  if (install_open_filter(control_fd) != 0) _exit(125);
  close(control_fd);
  if (diagnostics) fputs("METADATA_BROKER_EXEC_ATTEMPT\n", stderr);
  execvp(command[0], command);
  if (diagnostics) fprintf(stderr, "METADATA_BROKER_EXEC_ERROR errno=%d\n", errno);
  _exit(127);
}

static int broker_run(unsigned timeout_seconds, char **command) {
  sigset_t monitored_signals, original_mask;
  sigemptyset(&monitored_signals);
  sigaddset(&monitored_signals, SIGINT);
  sigaddset(&monitored_signals, SIGTERM);
  sigaddset(&monitored_signals, SIGHUP);
  if (sigprocmask(SIG_BLOCK, &monitored_signals, &original_mask) != 0) return 125;
  int channel[2];
  if (socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0, channel) != 0) {
    (void)sigprocmask(SIG_SETMASK, &original_mask, NULL);
    return 125;
  }
  pid_t expected_parent = getpid();
  pid_t child = fork();
  if (child < 0) {
    close(channel[0]); close(channel[1]);
    (void)sigprocmask(SIG_SETMASK, &original_mask, NULL);
    return 125;
  }
  if (child == 0) {
    close(channel[0]);
    struct sigaction alarm_default = {0};
    alarm_default.sa_handler = SIG_DFL;
    sigemptyset(&alarm_default.sa_mask);
    (void)sigaction(SIGALRM, &alarm_default, NULL);
    (void)sigprocmask(SIG_SETMASK, &original_mask, NULL);
    child_exec(channel[1], command, expected_parent);
  }
  close(channel[1]);
  int channel_flags = fcntl(channel[0], F_GETFL);
  if (channel_flags < 0 || fcntl(channel[0], F_SETFL, channel_flags | O_NONBLOCK) != 0) {
    kill_owned_child(child, KILL_SETUP);
    int ignored_status;
    (void)reap_child_bounded(child, &ignored_status, 1000u);
    close(channel[0]);
    return 125;
  }
  struct sigaction action = {0};
  action.sa_handler = remember_signal;
  sigemptyset(&action.sa_mask);
  if (sigaction(SIGINT, &action, NULL) != 0 ||
      sigaction(SIGTERM, &action, NULL) != 0 ||
      sigaction(SIGHUP, &action, NULL) != 0 ||
      sigprocmask(SIG_SETMASK, &original_mask, NULL) != 0) {
    kill_owned_child(child, KILL_SETUP);
    int ignored_status;
    (void)reap_child_bounded(child, &ignored_status, 1000u);
    close(channel[0]);
    return 125;
  }

  struct pollfd channel_poll = {.fd = channel[0], .events = POLLIN};
  int64_t setup_deadline = monotonic_milliseconds() + 1000;
  int listener = -1;
  for (;;) {
    int ready = poll(&channel_poll, 1, NOTIFICATION_POLL_MS);
    if (ready > 0 && (channel_poll.revents & POLLIN) != 0) {
      listener = receive_listener(channel[0]);
      if (listener >= 0) break;
      if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) continue;
      break;
    }
    if (ready > 0 && (channel_poll.revents & (POLLERR | POLLHUP | POLLNVAL)) != 0)
      break;
    if (ready < 0 && errno != EINTR) break;
    if (caught_signal != 0) {
      int forwarded = (int)caught_signal;
      kill(child, forwarded);
      int ignored_status;
      if (!reap_child_bounded(child, &ignored_status, SIGNAL_GRACE_MS)) {
        kill_owned_child(child, KILL_SETUP);
        (void)reap_child_bounded(child, &ignored_status, 1000u);
      }
      close(channel[0]);
      return 128 + forwarded;
    }
    if (monotonic_milliseconds() >= setup_deadline) break;
  }
  if (listener < 0) {
    kill_owned_child(child, KILL_SETUP);
    int ignored_status;
    (void)reap_child_bounded(child, &ignored_status, 1000u);
    close(channel[0]);
    return 125;
  }
  close(channel[0]);
  int listener_flags = fcntl(listener, F_GETFL);
  if (listener_flags < 0 || fcntl(listener, F_SETFL, listener_flags | O_NONBLOCK) != 0) {
    kill_owned_child(child, KILL_SETUP);
    int ignored_status;
    (void)reap_child_bounded(child, &ignored_status, 1000u);
    close(listener);
    return 125;
  }

  struct sigaction alarm_action = {0}, original_alarm_action;
  alarm_action.sa_handler = interrupt_wait;
  sigemptyset(&alarm_action.sa_mask);
  struct itimerval timer = {0}, original_timer;
  timer.it_value.tv_sec = (time_t)timeout_seconds;
  if (sigaction(SIGALRM, &alarm_action, &original_alarm_action) != 0) {
    kill_owned_child(child, KILL_SETUP);
    int ignored_status;
    (void)reap_child_bounded(child, &ignored_status, 1000u);
    close(listener);
    return 125;
  }
  sigset_t supervision_mask = original_mask;
  sigdelset(&supervision_mask, SIGALRM);
  if (sigprocmask(SIG_SETMASK, &supervision_mask, NULL) != 0) {
    (void)sigaction(SIGALRM, &original_alarm_action, NULL);
    kill_owned_child(child, KILL_SETUP);
    int ignored_status;
    (void)reap_child_bounded(child, &ignored_status, 1000u);
    close(listener);
    return 125;
  }
  if (setitimer(ITIMER_REAL, &timer, &original_timer) != 0) {
    (void)sigaction(SIGALRM, &original_alarm_action, NULL);
    (void)sigprocmask(SIG_SETMASK, &original_mask, NULL);
    kill_owned_child(child, KILL_SETUP);
    int ignored_status;
    (void)reap_child_bounded(child, &ignored_status, 1000u);
    close(listener);
    return 125;
  }

  char path_buffer[PATH_MAX];
  int64_t started = monotonic_milliseconds();
  int64_t deadline = started < 0 ? -1 : started + (int64_t)timeout_seconds * 1000;
  operation_deadline = deadline;
  int64_t signal_deadline = -1;
  int child_status = 0;
  bool child_done = false;
  bool timed_out = false;
  bool listener_dead = false;
  int64_t kill_deadline = -1;
  for (;;) {
    pid_t waited = waitpid(child, &child_status, WNOHANG);
    if (waited == child) { child_done = true; break; }
    if (waited < 0 && errno != EINTR) {
      child_status = 125 << 8;
      kill_owned_child(child, KILL_WAIT);
      child_done = reap_child_bounded(child, &child_status, 1000u);
      break;
    }
    int64_t now = monotonic_milliseconds();
    if (now < 0) { kill_owned_child(child, KILL_CLOCK); timed_out = true; }
    if (caught_signal != 0) {
      kill(child, (int)caught_signal);
      if (signal_deadline < 0) signal_deadline = now + SIGNAL_GRACE_MS;
    }
    if (deadline >= 0 && now >= deadline) {
      timed_out = true;
      if (signal_deadline < 0) {
        kill(child, SIGTERM);
        signal_deadline = now + SIGNAL_GRACE_MS;
      }
    }
    if (signal_deadline >= 0 && now >= signal_deadline && kill_deadline < 0) {
      kill_owned_child(child, KILL_GRACE);
      kill_deadline = now + 1000;
    }
    if (kill_deadline >= 0 && now >= kill_deadline) {
      child_status = 125 << 8;
      break;
    }

    if (kill_reason != KILL_NONE && kill_deadline < 0)
      kill_deadline = now + 1000;
    struct pollfd poll_fd = {.fd = listener_dead || signal_deadline >= 0 || kill_reason != KILL_NONE ? -1 : listener, .events = POLLIN};
    int ready = poll(&poll_fd, 1, NOTIFICATION_POLL_MS);
    if (ready < 0) {
      if (errno == EINTR) continue;
      last_control_errno = errno;
      kill_owned_child(child, KILL_LISTENER);
      listener_dead = true;
      continue;
    }
    if (ready > 0 && (poll_fd.revents & POLLIN) != 0) {
      struct seccomp_notif request;
      memset(&request, 0, sizeof(request));
      int received = -1;
      if (arm_operation_alarm(100u) == 0)
        received = ioctl(listener, SECCOMP_IOCTL_NOTIF_RECV, &request);
      int receive_error = errno;
      int armed = arm_operation_alarm(0u);
      if (armed < 0) {
        last_control_errno = errno;
        if (errno == ETIMEDOUT) timed_out = true;
        kill_owned_child(child, KILL_CONTROL);
      } else if (received == 0) {
        if (handle_notification(listener, &request, path_buffer) < 0 && errno != ENOENT) {
          if (errno == ETIMEDOUT) timed_out = true;
          kill_owned_child(child, atomic_grant_failed ? KILL_ATOMIC_GRANT : KILL_CONTROL);
        }
      } else if (receive_error != EINTR && receive_error != ENOENT && receive_error != EAGAIN) {
        last_control_errno = receive_error;
        kill_owned_child(child, KILL_RECV);
      }
    }
    if ((poll_fd.revents & POLLNVAL) != 0) {
      last_control_errno = EBADF;
      kill_owned_child(child, KILL_LISTENER);
      listener_dead = true;
    } else if ((poll_fd.revents & POLLHUP) != 0) {
      /* Filter users are gone before waitpid necessarily observes process
       * exit. Stop receiving and allow bounded reaping, not an immediate kill
       * that would falsely label an ordinary exit as supervisor termination. */
      listener_dead = true;
      if (kill_deadline < 0) kill_deadline = now + 1000;
    } else if ((poll_fd.revents & POLLERR) != 0) {
      /* seccomp_notify_poll returns EPOLLERR if its interruptible lock was
       * interrupted. Retry with a bounded backoff and the same deadline. */
      (void)poll(NULL, 0, 10);
    }
  }
  restore_alarm_state(&original_alarm_action, &original_timer, &original_mask);
  close(listener);
  if (!child_done) {
    kill_owned_child(child, KILL_CLEANUP);
    child_done = reap_child_bounded(child, &child_status, 1000u);
  }
  if (!child_done) return 125;
  if (WIFSIGNALED(child_status)) child_signal = WTERMSIG(child_status);
  if (timed_out) return 124;
  if (caught_signal != 0) return 128 + (int)caught_signal;
  if (WIFEXITED(child_status)) return WEXITSTATUS(child_status);
  if (WIFSIGNALED(child_status)) return 128 + WTERMSIG(child_status);
  return 125;
}

int main(int argc, char **argv) {
  unsigned timeout = 10u;
  int index = 1;
  if (index < argc && strcmp(argv[index], "--diagnostics") == 0) {
    diagnostics = true;
    ++index;
  }
  if (index < argc && strcmp(argv[index], "--timeout") == 0) {
    if (++index >= argc) { fputs("invalid arguments\n", stderr); return 2; }
    const char *digits = argv[index++];
    unsigned parsed = 0u;
    bool valid = digits[0] != '\0';
    for (; valid && *digits != '\0'; ++digits) {
      if (*digits < '0' || *digits > '9') { valid = false; break; }
      parsed = parsed * 10u + (unsigned)(*digits - '0');
      if (parsed > MAX_TIMEOUT_SECONDS) { valid = false; break; }
    }
    if (!valid || parsed == 0u) {
      fputs("invalid arguments\n", stderr); return 2;
    }
    timeout = (unsigned)parsed;
  }
  if (index >= argc || strcmp(argv[index], "--") != 0 || index + 1 >= argc) {
    fputs("usage: readonly_metadata_broker [--diagnostics] [--timeout seconds] -- program [args...]\n", stderr);
    return 2;
  }
  int result = broker_run(timeout, &argv[index + 1]);
  if (diagnostics)
    fprintf(stderr, "METADATA_BROKER exit=%d notified=%llu continued=%llu "
                    "protected=%llu mediated=%llu path_errors=%llu last_path_errno=%d "
                    "kill_reason=%d last_control_errno=%d child_signal=%d\n",
            result, (unsigned long long)notified, (unsigned long long)continued,
            (unsigned long long)protected_opens, (unsigned long long)mediated,
            (unsigned long long)path_errors, last_path_error,
            (int)kill_reason, last_control_errno, child_signal);
  return result;
}
