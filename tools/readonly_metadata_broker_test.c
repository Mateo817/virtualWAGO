#define _GNU_SOURCE
/* Native supervisor tests only: no protected file or hardware access. */
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#ifdef VIRTUALWAGO_METADATA_TEST_FILE
#define SYNTHETIC_METADATA_PATH VIRTUALWAGO_METADATA_TEST_FILE

static int probe_synthetic_readonly_file(void) {
  int rw_fd = open(SYNTHETIC_METADATA_PATH, O_RDWR);
  if (rw_fd < 0 || (fcntl(rw_fd, F_GETFD) & FD_CLOEXEC) != 0) return 51;
  char first = 0;
  if (read(rw_fd, &first, 1u) != 1) return 52;
  errno = 0;
  if (write(rw_fd, "x", 1u) >= 0 || errno != EBADF) return 53;

  int second_fd = open(SYNTHETIC_METADATA_PATH, O_RDONLY | O_CLOEXEC);
  if (second_fd < 0 || (fcntl(second_fd, F_GETFD) & FD_CLOEXEC) == 0) return 54;
  char second = 0;
  if (read(second_fd, &second, 1u) != 1 || second != first) return 55;

  char proc_path[64];
  int length = snprintf(proc_path, sizeof(proc_path), "/proc/self/fd/%d", rw_fd);
  if (length <= 0 || (size_t)length >= sizeof(proc_path)) return 56;
  int reopened = open(proc_path, O_RDWR);
  if (reopened >= 0) {
    close(reopened);
    return 57;
  }
  if (errno != EROFS && errno != EACCES) {
    return 58;
  }
  close(second_fd);
  close(rw_fd);
  return 0;
}
#endif

/* Sustained own-file traffic exceeds the old 100 ms alarm interval. The
 * protected variant repeatedly verifies the injected descriptor cannot write.
 * Unrelated traffic always uses /dev/null, never a hardware endpoint. */
static int stress_own_opens(bool protected_file) {
  struct timespec started, now;
  if (clock_gettime(CLOCK_MONOTONIC, &started) != 0) return 61;
  unsigned opens = 0u;
  for (;;) {
    int fd = open("/dev/null", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return 62;
    close(fd);
#ifdef VIRTUALWAGO_METADATA_TEST_FILE
    if (protected_file && probe_synthetic_readonly_file() != 0) return 63;
#else
    if (protected_file) return 64;
#endif
    if (++opens > 10000000u) return 65;
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0) return 66;
    int64_t elapsed = (int64_t)(now.tv_sec - started.tv_sec) * 1000 +
                      (int64_t)(now.tv_nsec - started.tv_nsec) / 1000000;
    if (elapsed >= 650) break;
  }
  return opens >= 2u ? 0 : 67;
}

static int run_broker(const char *broker, const char *timeout,
                      char *const child_argv[], unsigned *elapsed_ms) {
  struct timespec before, after;
  assert(clock_gettime(CLOCK_MONOTONIC, &before) == 0);
  pid_t runner = fork();
  assert(runner >= 0);
  if (runner == 0) {
    size_t count = 0;
    while (child_argv[count] != NULL && count < 100u) ++count;
    if (count == 0u || count > 100u) _exit(126);
    char **full = calloc(count + 5u, sizeof(char *));
    if (full == NULL) _exit(126);
    full[0] = (char *)broker; full[1] = "--timeout";
    full[2] = (char *)timeout; full[3] = "--";
    for (size_t i = 0; i < count; ++i) full[i + 4u] = child_argv[i];
    execv(broker, full);
    _exit(126);
  }
  int status = 0;
  while (waitpid(runner, &status, 0) < 0) assert(errno == EINTR);
  assert(clock_gettime(CLOCK_MONOTONIC, &after) == 0);
  int64_t elapsed = (int64_t)(after.tv_sec - before.tv_sec) * 1000 +
                    (int64_t)(after.tv_nsec - before.tv_nsec) / 1000000;
  *elapsed_ms = elapsed < 0 ? 0u : (unsigned)elapsed;
  assert(WIFEXITED(status));
  return WEXITSTATUS(status);
}

static void test_signal_forwarding(const char *broker) {
  pid_t runner = fork();
  assert(runner >= 0);
  if (runner == 0) {
    execl(broker, broker, "--timeout", "5", "--", "/bin/sleep", "5",
          (char *)NULL);
    _exit(126);
  }
  struct timespec startup = {0, 250000000L};
  while (nanosleep(&startup, &startup) != 0) assert(errno == EINTR);
  assert(kill(runner, SIGTERM) == 0);
  int status = 0;
  while (waitpid(runner, &status, 0) < 0) assert(errno == EINTR);
  assert(WIFEXITED(status) && WEXITSTATUS(status) == 128 + SIGTERM);
}

int main(int argc, char **argv) {
  if (argc == 2 && strcmp(argv[1], "--stress-unprotected") == 0)
    return stress_own_opens(false);
  if (argc == 2 && strcmp(argv[1], "--stress-protected") == 0)
    return stress_own_opens(true);
  if (argc == 2 && strcmp(argv[1], "--self-kill") == 0) {
    raise(SIGKILL);
    return 68;
  }
#ifdef VIRTUALWAGO_METADATA_TEST_FILE
  if (argc == 2 && strcmp(argv[1], "--probe-readonly") == 0)
    return probe_synthetic_readonly_file();
#endif
  if (argc == 2 && strcmp(argv[1], "--ignore-term") == 0) {
    signal(SIGTERM, SIG_IGN);
    struct timespec wait = {5, 0};
    while (nanosleep(&wait, &wait) != 0 && errno == EINTR) {}
    return 0;
  }
  assert(argc == 2);
  unsigned elapsed = 0;
  char *success_command[] = {"/bin/sh", "-c", "exit 23", NULL};
  int result = run_broker(argv[1], "3", success_command, &elapsed);
  if (result == 125) {
    /* Kernel/configuration may disable seccomp user notification. */
    puts("READONLY_METADATA_BROKER_TEST: SKIP (user notification unavailable)");
    return 77;
  }
  assert(result == 23);

  char *timeout_command[] = {"/bin/sleep", "5", NULL};
  result = run_broker(argv[1], "1", timeout_command, &elapsed);
  assert(result == 124);
  assert(elapsed < 2500u);
  char *ignore_term_command[] = {argv[0], "--ignore-term", NULL};
  result = run_broker(argv[1], "1", ignore_term_command, &elapsed);
  assert(result == 124);
  assert(elapsed >= 1000u && elapsed < 2500u);
  test_signal_forwarding(argv[1]);

  pid_t invalid = fork();
  assert(invalid >= 0);
  if (invalid == 0) {
    execl(argv[1], argv[1], "--timeout", "31", "--", "/bin/true", (char *)NULL);
    _exit(126);
  }
  int status = 0;
  while (waitpid(invalid, &status, 0) < 0) assert(errno == EINTR);
  assert(WIFEXITED(status) && WEXITSTATUS(status) == 2);
  puts("READONLY_METADATA_BROKER_TEST: PASS (native supervisor bounds only)");
  return 0;
}
