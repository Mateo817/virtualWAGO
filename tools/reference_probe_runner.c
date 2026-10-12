/* Own bounded namespace witness on the reference Linux host.
 * Connects only to its own loopback and abstract-Unix listeners. No PLC API.
 * Usage: runner guest-probe host-sentinel -- bwrap [namespace options...]
 */
#define _GNU_SOURCE
#include <assert.h>
#include <arpa/inet.h>
#include <errno.h>
#include <poll.h>
#include <signal.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static long long monotonic_ms(void) {
  struct timespec now;
  assert(clock_gettime(CLOCK_MONOTONIC, &now) == 0);
  return (long long)now.tv_sec * 1000 + now.tv_nsec / 1000000;
}

static void verify_baseline(int listener, int family, void *address, socklen_t size) {
  int client = socket(family, SOCK_STREAM | SOCK_CLOEXEC, 0);
  assert(client >= 0 && connect(client, address, size) == 0);
  int accepted = accept4(listener, NULL, NULL, SOCK_CLOEXEC);
  assert(accepted >= 0); close(accepted); close(client);
}

int main(int argc, char **argv) {
  if (argc < 6 || strcmp(argv[3], "--") != 0 || argv[4][0] != '/') return 2;
  struct stat sentinel;
  if (lstat(argv[2], &sentinel) != 0 || !S_ISREG(sentinel.st_mode)) return 2;
  int tcp = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0);
  struct sockaddr_in address = {.sin_family = AF_INET};
  address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
  assert(tcp >= 0 && bind(tcp, (struct sockaddr *)&address, sizeof(address)) == 0);
  assert(listen(tcp, 2) == 0);
  socklen_t address_size = sizeof(address);
  assert(getsockname(tcp, (struct sockaddr *)&address, &address_size) == 0);
  struct sockaddr_un local = {.sun_family = AF_UNIX};
  char name[80]; snprintf(name, sizeof(name), "virtualwago-proof-%ld", (long)getpid());
  memcpy(local.sun_path + 1, name, strlen(name));
  socklen_t local_size = (socklen_t)(offsetof(struct sockaddr_un, sun_path) + 1 + strlen(name));
  int unix_fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0);
  assert(unix_fd >= 0 && bind(unix_fd, (struct sockaddr *)&local, local_size) == 0);
  assert(listen(unix_fd, 2) == 0);
  verify_baseline(tcp, AF_INET, &address, address_size);
  verify_baseline(unix_fd, AF_UNIX, &local, local_size);
  const char *names[] = {"mnt", "net", "ipc", "pid", "user"};
  char namespace_values[5][32];
  for (int i = 0; i < 5; ++i) {
    char path[64]; struct stat info;
    snprintf(path, sizeof(path), "/proc/self/ns/%s", names[i]);
    assert(stat(path, &info) == 0);
    snprintf(namespace_values[i], sizeof(namespace_values[i]), "%llu", (unsigned long long)info.st_ino);
  }
  char port[16]; snprintf(port, sizeof(port), "%u", (unsigned)ntohs(address.sin_port));
  char **child_argv = calloc((size_t)argc + 10u, sizeof(char *));
  assert(child_argv != NULL);
  int n = 0;
  for (int i = 4; i < argc; ++i) child_argv[n++] = argv[i];
  child_argv[n++] = argv[1]; child_argv[n++] = argv[2];
  for (int i = 0; i < 5; ++i) child_argv[n++] = namespace_values[i];
  child_argv[n++] = port; child_argv[n++] = name;
  pid_t child = fork(); assert(child >= 0);
  if (child == 0) {
    close(tcp); close(unix_fd);
    if (setsid() < 0) _exit(2);
    execv(child_argv[0], child_argv); _exit(2);
  }
  int status = 0;
  long long deadline = monotonic_ms() + 15000;
  for (;;) {
    pid_t done = waitpid(child, &status, WNOHANG);
    if (done == child) break;
    assert(done == 0 || (done < 0 && errno == EINTR));
    if (monotonic_ms() >= deadline) {
      kill(-child, SIGKILL); kill(child, SIGKILL); waitpid(child, &status, 0);
      close(tcp); close(unix_fd); free(child_argv); return 2;
    }
    struct timespec pause = {0, 20000000L}; nanosleep(&pause, NULL);
  }
  int reached = 0;
  int accepted = accept4(tcp, NULL, NULL, SOCK_CLOEXEC);
  if (accepted >= 0) { ++reached; close(accepted); }
  accepted = accept4(unix_fd, NULL, NULL, SOCK_CLOEXEC);
  if (accepted >= 0) { ++reached; close(accepted); }
  close(tcp); close(unix_fd); free(child_argv);
  printf("OWN_WITNESS baseline=PASS listeners_reached=%d\n", reached);
  if (reached || !WIFEXITED(status)) return 2;
  return WEXITSTATUS(status);
}
