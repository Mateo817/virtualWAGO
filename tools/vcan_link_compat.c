/* Experimental libsocketcan boundary for an isolated virtual CAN link.
 * This accepts configuration metadata; it does not simulate CAN wire timing,
 * arbitration, bus-off, CANopen nodes, or DALI responses.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <linux/can/netlink.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <net/if.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include "vcan_link_kind.h"

static int configure(const char *symbol, const char *name, uint32_t value,
                     uint32_t supported)
{
    if (vcan_flags(name, NULL)) {
        if (value != supported) {
            errno = EOPNOTSUPP;
            return -1;
        }
        fprintf(stderr, "VW_VCAN_METADATA %s %s %u\n", symbol, name, value);
        return 0;
    }
    int (*original)(const char *, uint32_t) = dlsym(RTLD_NEXT, symbol);
    if (!original) {
        errno = ENOSYS;
        return -1;
    }
    return original(name, value);
}

int can_set_bitrate(const char *name, uint32_t bitrate)
{
    return configure("can_set_bitrate", name, bitrate, 125000);
}

int can_set_restart_ms(const char *name, uint32_t interval)
{
    return configure("can_set_restart_ms", name, interval, 2000);
}

/* vcan has link UP/DOWN but no physical controller error counters. This
 * explicitly limited projection supplies no arbitration or bus-off model. */
int can_get_state(const char *name, int *state)
{
    if (!state) {
        errno = EINVAL;
        return -1;
    }
    unsigned flags;
    if (vcan_flags(name, &flags)) {
        *state = flags & IFF_UP ? CAN_STATE_ERROR_ACTIVE : CAN_STATE_STOPPED;
        return 0;
    }
    int (*original)(const char *, int *) = dlsym(RTLD_NEXT, "can_get_state");
    if (!original) {
        errno = ENOSYS;
        return -1;
    }
    return original(name, state);
}
