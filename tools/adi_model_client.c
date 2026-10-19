/* Own local model-protocol client. No vendor, PLC, bus or network API. */
#define _GNU_SOURCE
#include <errno.h>
#include <poll.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

int main(int argc, char **argv) {
  struct sockaddr_un address = {.sun_family = AF_UNIX};
  if (argc != 2 || argv[1][0] != '/' ||
      strlen(argv[1]) >= sizeof(address.sun_path)) return 2;
  strcpy(address.sun_path, argv[1]);
  int fd = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC | SOCK_NONBLOCK, 0);
  if (fd < 0) return 2;
  if (connect(fd, (struct sockaddr *)&address,
              (socklen_t)(offsetof(struct sockaddr_un, sun_path) +
                          strlen(address.sun_path) + 1u)) != 0) {
    perror("own model connect"); close(fd); return 2;
  }
  char request[602];
  while (fgets(request, sizeof(request), stdin) != NULL) {
    size_t length = strlen(request);
    if (length && request[length - 1u] == '\n') request[--length] = '\0';
    if (length == 0 || length > 600 || strchr(request, '\r') != NULL) {
      close(fd); return 2;
    }
    struct pollfd ready = {.fd = fd, .events = POLLOUT};
    int result;
    do { result = poll(&ready, 1, 1000); } while (result < 0 && errno == EINTR);
    if (result <= 0 || !(ready.revents & POLLOUT) ||
        send(fd, request, length, MSG_NOSIGNAL) != (ssize_t)length) {
      close(fd); return 2;
    }
    ready.events = POLLIN; ready.revents = 0;
    do { result = poll(&ready, 1, 1000); } while (result < 0 && errno == EINTR);
    char response[4097];
    if (result <= 0 || !(ready.revents & POLLIN)) { close(fd); return 2; }
    ssize_t received = recv(fd, response, sizeof(response), MSG_TRUNC);
    if (received <= 0 || received > 4096) { close(fd); return 2; }
    response[received] = '\0';
    puts(response); fflush(stdout);
    if (strncmp(response, "ERR ", 4) == 0 ||
        strcmp(response, "NOT_READY") == 0) { close(fd); return 1; }
  }
  int result = ferror(stdin) ? 2 : 0;
  close(fd);
  return result;
}
