/* Run only inside a dedicated network namespace with a vcan named can0.
 * Calls on lo and a nonexistent interface must reach the genuine library and
 * fail. This probe never creates an interface or starts a CAN controller.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <linux/can/netlink.h>
#include <stdint.h>
#include <stdio.h>
#include "vcan_link_kind.h"

int main(int argc, char **argv)
{
    (void)argv;
    /* Fail closed before any potentially mutating library call. The dedicated
     * network namespace must contain only loopback and this kernel vcan. */
    if (!vcan_flags("can0", NULL) || if_nametoindex("vw-missing") != 0)
        return 10;
    struct if_nameindex *interfaces = if_nameindex();
    if (!interfaces)
        return 10;
    int isolated = 1;
    for (struct if_nameindex *i = interfaces; i->if_index; ++i)
        if (strcmp(i->if_name, "lo") && strcmp(i->if_name, "can0"))
            isolated = 0;
    if_freenameindex(interfaces);
    if (!isolated)
        return 10;
    void *library = dlopen("libsocketcan.so.2", RTLD_NOW | RTLD_GLOBAL);
    if (!library) {
        fprintf(stderr, "%s\n", dlerror());
        return 2;
    }
    int (*bitrate)(const char *, uint32_t) =
        dlsym(RTLD_DEFAULT, "can_set_bitrate");
    int (*restart)(const char *, uint32_t) =
        dlsym(RTLD_DEFAULT, "can_set_restart_ms");
    int (*get_state)(const char *, int *) =
        dlsym(RTLD_DEFAULT, "can_get_state");
    if (!bitrate || !restart || !get_state)
        return 2;
    if (bitrate("can0", 125000) != 0 || restart("can0", 2000) != 0)
        return 3;
    errno = 0;
    if (bitrate("can0", 250000) != -1 || errno != EOPNOTSUPP)
        return 4;
    errno = 0;
    if (restart("can0", 1000) != -1 || errno != EOPNOTSUPP)
        return 5;
    if (bitrate("lo", 125000) == 0 ||
        bitrate("vw-missing", 125000) == 0)
        return 6;
    int state = -1;
    int expected = argc > 1 ? CAN_STATE_ERROR_ACTIVE : CAN_STATE_STOPPED;
    if (get_state("can0", &state) != 0 || state != expected)
        return 7;
    errno = 0;
    if (get_state("can0", NULL) != -1 || errno != EINVAL)
        return 8;
    if (get_state("lo", &state) == 0)
        return 9;
    puts("VCAN_COMPAT_PROBE_PASS");
    dlclose(library);
    return 0;
}
