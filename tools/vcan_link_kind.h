/* Shared read-only kernel link-kind query for adapter and probe. */
#ifndef VW_VCAN_LINK_KIND_H
#define VW_VCAN_LINK_KIND_H
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <net/if.h>
#include <poll.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
/* Never infer vcan from an interface name or ARPHRD_CAN alone. */
static int vcan_flags(const char *name, unsigned *flags)
{
    if (!name || strcmp(name, "can0") != 0)
        return 0;
    unsigned index = if_nametoindex(name);
    if (!index)
        return 0;
    int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
    if (fd < 0)
        return 0;
    struct {
        struct nlmsghdr header;
        struct ifinfomsg link;
    } request = {
        .header = {.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg)),
                   .nlmsg_type = RTM_GETLINK, .nlmsg_flags = NLM_F_REQUEST,
                   .nlmsg_seq = 1},
        .link = {.ifi_family = AF_UNSPEC, .ifi_index = (int)index}
    };
    struct sockaddr_nl kernel = {.nl_family = AF_NETLINK};
    int found = 0;
    if (sendto(fd, &request, sizeof(request), 0,
               (struct sockaddr *)&kernel, sizeof(kernel)) != sizeof(request))
        goto done;
    struct pollfd pending = {.fd = fd, .events = POLLIN};
    if (poll(&pending, 1, 250) <= 0)
        goto done;
    union { struct nlmsghdr align; unsigned char bytes[8192]; } buffer;
    struct sockaddr_nl sender = {0};
    socklen_t sender_len = sizeof(sender);
    ssize_t received = recvfrom(fd, buffer.bytes, sizeof(buffer.bytes), 0,
                               (struct sockaddr *)&sender, &sender_len);
    if (received <= 0 || sender.nl_pid != 0)
        goto done;
    int remaining = (int)received;
    for (struct nlmsghdr *h = (void *)buffer.bytes; NLMSG_OK(h, remaining);
         h = NLMSG_NEXT(h, remaining)) {
        if (h->nlmsg_seq != 1 || h->nlmsg_type != RTM_NEWLINK ||
            h->nlmsg_len < NLMSG_LENGTH(sizeof(struct ifinfomsg)))
            continue;
        struct ifinfomsg *link = NLMSG_DATA(h);
        if (link->ifi_index != (int)index)
            continue;
        int size = IFLA_PAYLOAD(h);
        for (struct rtattr *a = IFLA_RTA(link); RTA_OK(a, size);
             a = RTA_NEXT(a, size)) {
            if ((a->rta_type & NLA_TYPE_MASK) != IFLA_LINKINFO)
                continue;
            int nested = RTA_PAYLOAD(a);
            for (struct rtattr *b = RTA_DATA(a); RTA_OK(b, nested);
                 b = RTA_NEXT(b, nested))
                if ((b->rta_type & NLA_TYPE_MASK) == IFLA_INFO_KIND &&
                    RTA_PAYLOAD(b) == 5 && memcmp(RTA_DATA(b), "vcan", 5) == 0)
                    {
                        found = 1;
                        if (flags)
                            *flags = link->ifi_flags;
                    }
        }
    }
done:
    close(fd);
    return found;
}

#endif
