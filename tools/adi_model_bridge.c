#define _GNU_SOURCE

#include "adi_model_bridge.h"

#ifdef VIRTUALWAGO_ENABLE_MODEL_BRIDGE

#ifndef ADI_MODEL_BRIDGE_STANDALONE_TEST
#include <adi_digital_adapter.h>
#else
/* Native test hooks replace only the adapter API, never the socket code. */
int32_t virtual_adi_set_inputs(uint16_t input_bits);
int32_t virtual_adi_set_permit(bool permit);
#endif

#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <poll.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

#define BRIDGE_ENV "VIRTUALWAGO_MODEL_SOCKET"
#define REQUEST_MAX 64u
#define RESPONSE_MAX 512u
#define POLL_INTERVAL_MS 50
#define CLIENT_IDLE_MS 500
#define SEND_TIMEOUT_MS 100

static pthread_mutex_t bridge_control_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t bridge_control_cond = PTHREAD_COND_INITIALIZER;
static pthread_t bridge_worker;
static bool bridge_worker_started;
static bool bridge_stopping;
static atomic_bool bridge_stop_requested;
static atomic_bool bridge_worker_failed;
static int bridge_listener_fd = -1;
static int bridge_wake_read_fd = -1;
static int bridge_wake_write_fd = -1;
static int bridge_parent_fd = -1;
static char bridge_socket_path[sizeof(((struct sockaddr_un *)0)->sun_path)];
static char bridge_parent_path[sizeof(((struct sockaddr_un *)0)->sun_path)];
static char bridge_socket_name[sizeof(((struct sockaddr_un *)0)->sun_path)];
static dev_t bridge_socket_device;
static ino_t bridge_socket_inode;
static bool bridge_socket_identity_valid;

static int64_t monotonic_ms(void) {
  struct timespec now;
  if (clock_gettime(CLOCK_MONOTONIC, &now) != 0 || now.tv_sec < 0)
    return -1;
  return (int64_t)now.tv_sec * 1000 + (int64_t)now.tv_nsec / 1000000;
}

static bool same_directory_identity(const char *path, int directory_fd) {
  struct stat by_fd;
  struct stat by_path;
  if (fstat(directory_fd, &by_fd) != 0 || lstat(path, &by_path) != 0)
    return false;
  return S_ISDIR(by_path.st_mode) && by_fd.st_dev == by_path.st_dev &&
         by_fd.st_ino == by_path.st_ino;
}

/* Open every path component without following symlinks. Only the final
 * containing directory must be private; ancestors may be system-owned dirs.
 */
static int open_private_parent(const char *socket_path, char *socket_name,
                               size_t socket_name_capacity) {
  const size_t path_length = strlen(socket_path);
  if (path_length < 2u || path_length >= sizeof(bridge_socket_path) ||
      socket_path[0] != '/' || socket_path[path_length - 1u] == '/')
    return -1;

  const char *last_slash = strrchr(socket_path, '/');
  if (last_slash == NULL || last_slash[1] == '\0') return -1;
  const size_t name_length = strlen(last_slash + 1);
  if (name_length == 0u || name_length >= socket_name_capacity ||
      strchr(last_slash + 1, '/') != NULL)
    return -1;
  memcpy(socket_name, last_slash + 1, name_length + 1u);

  char parent_path[sizeof(bridge_socket_path)];
  size_t parent_length = (size_t)(last_slash - socket_path);
  if (parent_length == 0u) parent_length = 1u;
  memcpy(parent_path, socket_path, parent_length);
  parent_path[parent_length] = '\0';

  int directory_fd = open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC);
  if (directory_fd < 0) return -1;

  const char *cursor = socket_path + 1;
  const char *parent_end = socket_path + parent_length;
  while (cursor < parent_end) {
    const char *separator = memchr(cursor, '/', (size_t)(parent_end - cursor));
    const char *component_end = separator == NULL ? parent_end : separator;
    size_t component_length = (size_t)(component_end - cursor);
    if (component_length == 0u ||
        (component_length == 1u && cursor[0] == '.') ||
        (component_length == 2u && cursor[0] == '.' && cursor[1] == '.')) {
      close(directory_fd);
      return -1;
    }
    char component[sizeof(bridge_socket_path)];
    if (component_length >= sizeof(component)) {
      close(directory_fd);
      return -1;
    }
    memcpy(component, cursor, component_length);
    component[component_length] = '\0';
    int next_fd = openat(directory_fd, component,
                         O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    if (next_fd < 0) {
      close(directory_fd);
      return -1;
    }
    close(directory_fd);
    directory_fd = next_fd;
    cursor = component_end + (separator == NULL ? 0 : 1);
  }

  struct stat info;
  if (fstat(directory_fd, &info) != 0 || info.st_uid != geteuid() ||
      (info.st_mode & 0777u) != 0700u ||
      !same_directory_identity(parent_path, directory_fd)) {
    close(directory_fd);
    return -1;
  }
  return directory_fd;
}

static void remove_owned_socket(void) {
  if (bridge_parent_fd >= 0 && bridge_socket_identity_valid) {
    struct stat current;
    if (fstatat(bridge_parent_fd, bridge_socket_name, &current,
                AT_SYMLINK_NOFOLLOW) == 0 &&
        S_ISSOCK(current.st_mode) &&
        current.st_dev == bridge_socket_device &&
        current.st_ino == bridge_socket_inode)
      (void)unlinkat(bridge_parent_fd, bridge_socket_name, 0);
  }
  bridge_socket_identity_valid = false;
}

static void close_endpoint(void) {
  remove_owned_socket();
  if (bridge_listener_fd >= 0) close(bridge_listener_fd);
  if (bridge_wake_read_fd >= 0) close(bridge_wake_read_fd);
  if (bridge_wake_write_fd >= 0) close(bridge_wake_write_fd);
  if (bridge_parent_fd >= 0) close(bridge_parent_fd);
  bridge_listener_fd = -1;
  bridge_wake_read_fd = -1;
  bridge_wake_write_fd = -1;
  bridge_parent_fd = -1;
  bridge_socket_path[0] = '\0';
  bridge_parent_path[0] = '\0';
  bridge_socket_name[0] = '\0';
}

static int prepare_endpoint(const char *socket_path) {
  size_t length = strlen(socket_path);
  if (length < 2u || length >= sizeof(bridge_socket_path) ||
      socket_path[0] != '/' || socket_path[length - 1u] == '/') return -1;
  memcpy(bridge_socket_path, socket_path, length + 1u);
  const char *last_slash = strrchr(socket_path, '/');
  size_t parent_length = (size_t)(last_slash - socket_path);
  if (parent_length == 0u) parent_length = 1u;
  memcpy(bridge_parent_path, socket_path, parent_length);
  bridge_parent_path[parent_length] = '\0';
  bridge_parent_fd = open_private_parent(socket_path, bridge_socket_name,
                                         sizeof(bridge_socket_name));
  if (bridge_parent_fd < 0) return -1;

  struct stat existing;
  if (fstatat(bridge_parent_fd, bridge_socket_name, &existing,
              AT_SYMLINK_NOFOLLOW) == 0 || errno != ENOENT)
    return -1; /* Never remove or replace an existing path. */

  bridge_listener_fd = socket(AF_UNIX,
                              SOCK_SEQPACKET | SOCK_NONBLOCK | SOCK_CLOEXEC,
                              0);
  if (bridge_listener_fd < 0) return -1;
  struct sockaddr_un address;
  memset(&address, 0, sizeof(address));
  address.sun_family = AF_UNIX;
  memcpy(address.sun_path, socket_path, length + 1u);
  if (bind(bridge_listener_fd, (struct sockaddr *)&address,
           (socklen_t)(offsetof(struct sockaddr_un, sun_path) + length + 1u)) != 0)
    return -1;

  struct stat bound;
  if (fstatat(bridge_parent_fd, bridge_socket_name, &bound,
              AT_SYMLINK_NOFOLLOW) != 0 || !S_ISSOCK(bound.st_mode) ||
      bound.st_uid != geteuid())
    return -1;
  bridge_socket_device = bound.st_dev;
  bridge_socket_inode = bound.st_ino;
  bridge_socket_identity_valid = true;

  if (chmod(bridge_socket_path, 0600) != 0 ||
      fstatat(bridge_parent_fd, bridge_socket_name, &bound,
              AT_SYMLINK_NOFOLLOW) != 0 ||
      !S_ISSOCK(bound.st_mode) || bound.st_uid != geteuid() ||
      (bound.st_mode & 0777u) != 0600u ||
      bound.st_dev != bridge_socket_device ||
      bound.st_ino != bridge_socket_inode ||
      !same_directory_identity(bridge_parent_path, bridge_parent_fd))
    return -1;

  if (listen(bridge_listener_fd, 1) != 0) return -1;
  int wake_pipe[2];
  if (pipe2(wake_pipe, O_NONBLOCK | O_CLOEXEC) != 0) return -1;
  bridge_wake_read_fd = wake_pipe[0];
  bridge_wake_write_fd = wake_pipe[1];
  return 0;
}

static void drain_wake_pipe(void) {
  char buffer[32];
  while (read(bridge_wake_read_fd, buffer, sizeof(buffer)) > 0) {}
}

static bool wait_client_writable(int client_fd, int64_t deadline_ms) {
  while (!atomic_load(&bridge_stop_requested)) {
    int64_t now = monotonic_ms();
    if (now < 0 || now >= deadline_ms) return false;
    int64_t remaining = deadline_ms - now;
    int timeout = remaining < POLL_INTERVAL_MS ? (int)remaining : POLL_INTERVAL_MS;
    struct pollfd poll_fds[2];
    poll_fds[0].fd = bridge_wake_read_fd;
    poll_fds[0].events = POLLIN;
    poll_fds[0].revents = 0;
    poll_fds[1].fd = client_fd;
    poll_fds[1].events = POLLOUT;
    poll_fds[1].revents = 0;
    int result = poll(poll_fds, 2, timeout);
    if (result < 0 && errno == EINTR) continue;
    if (result <= 0) continue;
    if ((poll_fds[0].revents & POLLIN) != 0) {
      drain_wake_pipe();
      return false;
    }
    if ((poll_fds[1].revents & POLLOUT) != 0) return true;
    if ((poll_fds[1].revents & (POLLERR | POLLHUP | POLLNVAL)) != 0)
      return false;
  }
  return false;
}

static bool send_response(int client_fd, const char *response) {
  const size_t length = strlen(response);
  if (length == 0u || length > RESPONSE_MAX) return false;
  int64_t now = monotonic_ms();
  if (now < 0) return false;
  const int64_t deadline = now + SEND_TIMEOUT_MS;
  while (!atomic_load(&bridge_stop_requested)) {
    ssize_t sent = send(client_fd, response, length,
                        MSG_DONTWAIT | MSG_NOSIGNAL);
    if (sent == (ssize_t)length) return true;
    if (sent >= 0) return false; /* SOCK_SEQPACKET sends one complete record. */
    if (errno == EINTR) continue;
    if (errno != EAGAIN && errno != EWOULDBLOCK) return false;
    if (!wait_client_writable(client_fd, deadline)) return false;
  }
  return false;
}

static bool parse_input(const char *packet, size_t length, uint16_t *value) {
  static const char prefix[] = "INPUT ";
  if (length <= sizeof(prefix) - 1u || length > sizeof(prefix) - 1u + 3u ||
      memcmp(packet, prefix, sizeof(prefix) - 1u) != 0)
    return false;
  size_t digits = length - (sizeof(prefix) - 1u);
  if (digits > 1u && packet[sizeof(prefix) - 1u] == '0') return false;
  unsigned parsed = 0u;
  for (size_t index = sizeof(prefix) - 1u; index < length; ++index) {
    unsigned char byte = (unsigned char)packet[index];
    if (byte < '0' || byte > '9') return false;
    parsed = parsed * 10u + (unsigned)(byte - '0');
    if (parsed > 255u) return false;
  }
  *value = (uint16_t)parsed;
  return true;
}

static bool format_status(const virtual_model_snapshot *snapshot,
                          char *response, size_t capacity) {
  int count = snprintf(response, capacity,
                       "STATUS input=%u permit=%u requested=%u effective=%u watchdog=%u fault=%u generation=%llu frames=%llu opened=%u configured=%u running=%u",
                       (unsigned)(snapshot->inputs & 0x00ffu),
                       snapshot->permit ? 1u : 0u,
                       (unsigned)snapshot->requested_outputs,
                       (unsigned)snapshot->effective_outputs,
                       snapshot->watchdog_healthy ? 1u : 0u,
                       snapshot->fault_latched ? 1u : 0u,
                       (unsigned long long)snapshot->generation,
                       (unsigned long long)snapshot->frame_count,
                       snapshot->opened ? 1u : 0u,
                       snapshot->configured ? 1u : 0u,
                       snapshot->app_running ? 1u : 0u);
  return count > 0 && (size_t)count < capacity &&
         (size_t)count <= RESPONSE_MAX;
}

static bool process_packet(const char *packet, size_t length, char *response,
                           size_t response_capacity, bool *close_after) {
  *close_after = false;
  if (length == 6u && memcmp(packet, "STATUS", 6u) == 0) {
    virtual_model_snapshot snapshot;
    if (virtual_adi_model_snapshot(&snapshot) != 0) {
      strcpy(response, "ERR STATE");
      return true;
    }
    if (!snapshot.initialized) {
      strcpy(response, "NOT_READY");
      return true;
    }
    return format_status(&snapshot, response, response_capacity);
  }

  virtual_model_snapshot snapshot;
  if (virtual_adi_model_snapshot(&snapshot) != 0) {
    strcpy(response, "ERR STATE");
    return true;
  }
  if (!snapshot.initialized) {
    strcpy(response, "NOT_READY");
    return true;
  }

  uint16_t input_value;
  if (parse_input(packet, length, &input_value)) {
    if (virtual_adi_set_inputs(input_value) != 0) {
      strcpy(response, "ERR STATE");
      return true;
    }
    strcpy(response, "OK INPUT");
    return true;
  }
  if (length == 8u && memcmp(packet, "PERMIT 0", 8u) == 0) {
    if (virtual_adi_set_permit(false) != 0) {
      strcpy(response, "ERR STATE");
      return true;
    }
    strcpy(response, "OK PERMIT");
    return true;
  }
  if (length == 8u && memcmp(packet, "PERMIT 1", 8u) == 0) {
    if (virtual_adi_set_permit(true) != 0) {
      strcpy(response, "ERR STATE");
      return true;
    }
    strcpy(response, "OK PERMIT");
    return true;
  }
  if (length == 5u && memcmp(packet, "FAULT", 5u) == 0) {
    if (virtual_adi_latch_fault() != 0) {
      strcpy(response, "ERR STATE");
      return true;
    }
    strcpy(response, "OK FAULT LATCHED");
    return true;
  }
  strcpy(response, "ERR COMMAND");
  *close_after = true;
  return true;
}

static void disconnect_client(int client_fd) {
  if (client_fd >= 0) close(client_fd);
  /* The connection lease is separate from the ADI watchdog. */
  (void)virtual_adi_set_permit(false);
}

static int accept_same_euid_client(void) {
  int client_fd = accept4(bridge_listener_fd, NULL, NULL,
                          SOCK_NONBLOCK | SOCK_CLOEXEC);
  if (client_fd < 0) return -1;
  /* SO_PEERCRED limits access to this effective UID; it does not isolate
   * mutually untrusted processes that already run as the same UID.
   */
  struct ucred credentials;
  socklen_t credentials_size = sizeof(credentials);
  if (getsockopt(client_fd, SOL_SOCKET, SO_PEERCRED, &credentials,
                 &credentials_size) != 0 ||
      credentials_size != sizeof(credentials) ||
      credentials.uid != geteuid()) {
    close(client_fd);
    return -1;
  }
  return client_fd;
}

static bool handle_client(int client_fd) {
  int64_t last_activity = monotonic_ms();
  if (last_activity < 0) return false;
  while (!atomic_load(&bridge_stop_requested)) {
    int64_t now = monotonic_ms();
    if (now < 0 || now - last_activity >= CLIENT_IDLE_MS) return false;
    int64_t remaining = CLIENT_IDLE_MS - (now - last_activity);
    int timeout = remaining < POLL_INTERVAL_MS ? (int)remaining : POLL_INTERVAL_MS;
    struct pollfd poll_fds[2];
    poll_fds[0].fd = bridge_wake_read_fd;
    poll_fds[0].events = POLLIN;
    poll_fds[0].revents = 0;
    poll_fds[1].fd = client_fd;
    poll_fds[1].events = POLLIN;
    poll_fds[1].revents = 0;
    int ready = poll(poll_fds, 2, timeout);
    if (ready < 0 && errno == EINTR) continue;
    if (ready < 0) return false;
    if ((poll_fds[0].revents & POLLIN) != 0) {
      drain_wake_pipe();
      return false;
    }
    if (ready == 0) continue;
    if ((poll_fds[1].revents & POLLIN) != 0) {
      char packet[REQUEST_MAX];
      struct iovec vector;
      vector.iov_base = packet;
      vector.iov_len = sizeof(packet);
      struct msghdr message;
      memset(&message, 0, sizeof(message));
      message.msg_iov = &vector;
      message.msg_iovlen = 1u;
      ssize_t length = recvmsg(client_fd, &message, MSG_DONTWAIT);
      if (length <= 0) return false;
      last_activity = monotonic_ms();
      if (last_activity < 0) return false;
      if ((message.msg_flags & MSG_TRUNC) != 0 ||
          (size_t)length > sizeof(packet)) {
        (void)send_response(client_fd, "ERR TOO_LONG");
        return false;
      }
      char response[RESPONSE_MAX + 1u];
      bool close_after;
      if (!process_packet(packet, (size_t)length, response,
                          sizeof(response), &close_after) ||
          !send_response(client_fd, response) || close_after)
        return false;
    }
    if ((poll_fds[1].revents & (POLLERR | POLLHUP | POLLNVAL)) != 0)
      return false;
  }
  return false;
}

static void *bridge_worker_main(void *unused) {
  (void)unused;
  int client_fd = -1;
  bool fatal = false;
  while (!atomic_load(&bridge_stop_requested)) {
    struct pollfd poll_fds[2];
    poll_fds[0].fd = bridge_wake_read_fd;
    poll_fds[0].events = POLLIN;
    poll_fds[0].revents = 0;
    poll_fds[1].fd = bridge_listener_fd;
    poll_fds[1].events = POLLIN;
    poll_fds[1].revents = 0;
    int ready = poll(poll_fds, 2, POLL_INTERVAL_MS);
    if (ready < 0 && errno == EINTR) continue;
    if (ready < 0) {
      fatal = true;
      break;
    }
    if ((poll_fds[0].revents & POLLIN) != 0) {
      drain_wake_pipe();
      if (atomic_load(&bridge_stop_requested)) break;
    }
    if ((poll_fds[1].revents & (POLLERR | POLLHUP | POLLNVAL)) != 0) {
      fatal = true;
      break;
    }
    if ((poll_fds[1].revents & POLLIN) != 0) {
      client_fd = accept_same_euid_client();
      if (client_fd < 0) continue;
      (void)handle_client(client_fd);
      disconnect_client(client_fd);
      client_fd = -1;
    }
  }
  if (client_fd >= 0) disconnect_client(client_fd);
  if (fatal) {
    (void)virtual_adi_set_permit(false);
    atomic_store(&bridge_worker_failed, true);
  }
  return NULL;
}

int virtual_model_bridge_start(void) {
  if (pthread_mutex_lock(&bridge_control_mutex) != 0) return -1;
  if (bridge_stopping) {
    pthread_mutex_unlock(&bridge_control_mutex);
    return -1;
  }
  if (bridge_worker_started) {
    int32_t result = atomic_load(&bridge_worker_failed) ? -1 : 0;
    pthread_mutex_unlock(&bridge_control_mutex);
    return result;
  }

  const char *configured_path = getenv(BRIDGE_ENV);
  if (configured_path == NULL) {
    pthread_mutex_unlock(&bridge_control_mutex);
    return 0;
  }
  if (configured_path[0] == '\0' || prepare_endpoint(configured_path) != 0) {
    close_endpoint();
    pthread_mutex_unlock(&bridge_control_mutex);
    return -1;
  }

  atomic_store(&bridge_stop_requested, false);
  atomic_store(&bridge_worker_failed, false);
  int result = pthread_create(&bridge_worker, NULL, bridge_worker_main, NULL);
  if (result != 0) {
    close_endpoint();
    pthread_mutex_unlock(&bridge_control_mutex);
    return -1;
  }
  bridge_worker_started = true;
  pthread_mutex_unlock(&bridge_control_mutex);
  return 0;
}

void virtual_model_bridge_stop(void) {
  if (pthread_mutex_lock(&bridge_control_mutex) != 0) return;
  while (bridge_stopping)
    (void)pthread_cond_wait(&bridge_control_cond, &bridge_control_mutex);
  if (!bridge_worker_started) {
    pthread_mutex_unlock(&bridge_control_mutex);
    return;
  }
  bridge_stopping = true;
  atomic_store(&bridge_stop_requested, true);
  char wake = 'x';
  if (bridge_wake_write_fd >= 0)
    (void)write(bridge_wake_write_fd, &wake, 1u);
  pthread_t worker = bridge_worker;
  pthread_mutex_unlock(&bridge_control_mutex);

  int joined = pthread_join(worker, NULL);

  pthread_mutex_lock(&bridge_control_mutex);
  if (joined == 0) {
    close_endpoint();
    bridge_worker_started = false;
    atomic_store(&bridge_worker_failed, false);
  }
  bridge_stopping = false;
  pthread_cond_broadcast(&bridge_control_cond);
  pthread_mutex_unlock(&bridge_control_mutex);
}

__attribute__((destructor)) static void bridge_runtime_unload(void) {
  virtual_model_bridge_stop();
}

#else

int virtual_model_bridge_start(void) { return 0; }
void virtual_model_bridge_stop(void) {}

#endif
