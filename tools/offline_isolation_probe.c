/* Own bounded Linux/ARM carrier check; no WAGO, DAL or runtime calls.
 * Arguments are a private host sentinel path, host namespace inode numbers,
 * a live host loopback listener port and a live host abstract Unix socket name.
 * Only those controlled local listeners are attempted; no external destination.
 */
#define _DEFAULT_SOURCE
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <poll.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>

static int absent(const char *path)
{
    struct stat st;
    return lstat(path, &st) == -1 && errno == ENOENT;
}

static int distinct(const char *name, const char *original)
{
    char path[64];
    struct stat st;
    snprintf(path, sizeof path, "/proc/self/ns/%s", name);
    return stat(path, &st) == 0 && (uint64_t)st.st_ino != strtoull(original, NULL, 10);
}

static int status_is(const char *name, unsigned long expected, int base)
{
    char line[256];
    int okay = 0;
    FILE *status = fopen("/proc/self/status", "r");
    if (!status) return 0;
    while (fgets(line, sizeof line, status)) {
        if (strncmp(line, name, strlen(name)) == 0) {
            okay = strtoul(line + strlen(name), NULL, base) == expected;
            break;
        }
    }
    fclose(status);
    return okay;
}

static int connection_denied(int fd, const struct sockaddr *address, socklen_t length)
{
    if (fd < 0) return 0;
    if (connect(fd, address, length) == 0) return 0;
    if (errno != EINPROGRESS) return 1;
    /* Nonblocking loopback connect may begin asynchronously even when the
     * private namespace has no listener. Require the actual terminal error. */
    struct pollfd wait = {.fd = fd, .events = POLLOUT};
    if (poll(&wait, 1, 1000) <= 0) return 0;
    int error = 0;
    socklen_t size = sizeof error;
    return getsockopt(fd, SOL_SOCKET, SO_ERROR, &error, &size) == 0 && error != 0;
}

int main(int argc, char **argv)
{
    if (argc != 9) return 2;
    char *end;
    unsigned long port = strtoul(argv[7], &end, 10);
    if (*end || port == 0 || port > 65535 || strlen(argv[8]) > 100) return 2;
    int mount_private = distinct("mnt", argv[2]);
    int net_private = distinct("net", argv[3]);
    int ipc_private = distinct("ipc", argv[4]);
    int pid_private = distinct("pid", argv[5]);
    int user_private = distinct("user", argv[6]);
    int host_file_absent = absent(argv[1]);
    int hardware_absent = absent("/dev/kbus0") && absent("/dev/uio0") &&
        absent("/dev/eeprom") && absent("/dev/ttyKbus");
    int endpoints_absent = absent("/sys") && absent("/run/dbus/system_bus_socket") &&
        absent("/var/run/docker.sock") && absent("/home/developer");
    int fd = open("/opt/research/should-not-write", O_WRONLY | O_CREAT, 0600);
    int root_readonly = fd < 0 && errno == EROFS;
    if (fd >= 0) close(fd);
    int no_caps = status_is("CapEff:", 0, 16);
    int no_new_privs = status_is("NoNewPrivs:", 1, 10);
    int clean_env = getenv("LD_PRELOAD") == NULL && getenv("LD_LIBRARY_PATH") == NULL &&
        getenv("SSH_AUTH_SOCK") == NULL && getenv("DBUS_SYSTEM_BUS_ADDRESS") == NULL;

    struct sockaddr_in tcp = {.sin_family = AF_INET, .sin_port = htons((uint16_t)port)};
    tcp.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    fd = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0);
    int loopback_denied = connection_denied(fd, (struct sockaddr *)&tcp, sizeof tcp);
    if (fd >= 0) close(fd);

    struct sockaddr_un unix_addr = {.sun_family = AF_UNIX};
    memcpy(unix_addr.sun_path + 1, argv[8], strlen(argv[8]));
    fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC | SOCK_NONBLOCK, 0);
    int abstract_denied = connection_denied(fd, (struct sockaddr *)&unix_addr,
        (socklen_t)(offsetof(struct sockaddr_un, sun_path) + 1 + strlen(argv[8])));
    if (fd >= 0) close(fd);

    int okay = mount_private && net_private && ipc_private && pid_private && user_private &&
        host_file_absent && hardware_absent && endpoints_absent && root_readonly &&
        no_caps && no_new_privs && clean_env && loopback_denied && abstract_denied;
    printf("{\"scope\":\"own ARM probe; controlled local endpoints only\","
           "\"pass\":%d,\"mount_private\":%d,\"net_private\":%d,\"ipc_private\":%d,"
           "\"pid_private\":%d,\"user_private\":%d,\"host_file_absent\":%d,\"hardware_absent\":%d,"
           "\"endpoints_absent\":%d,\"root_readonly\":%d,\"no_caps\":%d,"
           "\"no_new_privs\":%d,\"clean_env\":%d,\"loopback_denied\":%d,\"abstract_denied\":%d}\n",
           okay, mount_private, net_private, ipc_private, pid_private, user_private, host_file_absent,
           hardware_absent, endpoints_absent, root_readonly, no_caps, no_new_privs,
           clean_env, loopback_denied, abstract_denied);
    return okay ? 0 : 1;
}
