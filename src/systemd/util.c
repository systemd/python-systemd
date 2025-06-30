/***
  This file is part of systemd.

  Copyright 2010 Lennart Poettering

  systemd is free software; you can redistribute it and/or modify it
  under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  systemd is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with systemd; If not, see <http://www.gnu.org/licenses/>.
***/

/* stuff imported from systemd without any changes */

#ifndef _GNU_SOURCE
#  define _GNU_SOURCE
#endif

#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>
#include <errno.h>
#include <endian.h>
#include <fcntl.h>
#include <unistd.h>
#include <net/if.h>

#include "util.h"

int safe_atou(const char *s, unsigned *ret_u) {
        char *x = NULL;
        unsigned long l;

        assert(s);
        assert(ret_u);

        /* strtoul() is happy to parse negative values, and silently
         * converts them to unsigned values without generating an
         * error. We want a clean error, hence let's look for the "-"
         * prefix on our own, and generate an error. But let's do so
         * only after strtoul() validated that the string is clean
         * otherwise, so that we return EINVAL preferably over
         * ERANGE. */

        errno = 0;
        l = strtoul(s, &x, 0);
        if (errno > 0)
                return -errno;
        if (!x || x == s || *x)
                return -EINVAL;
        if (s[0] == '-')
                return -ERANGE;
        if ((unsigned long) (unsigned) l != l)
                return -ERANGE;

        *ret_u = (unsigned) l;
        return 0;
}

static bool socket_ipv6_is_supported(void) {
        if (access("/proc/net/if_inet6", F_OK) != 0)
                return false;

        return true;
}

static int assign_address(const char *s,
                          uint16_t port,
                          union sockaddr_union *addr, unsigned *addr_len) {
        int r;

        /* IPv4 in w.x.y.z:p notation? */
        r = inet_pton(AF_INET, s, &addr->in.sin_addr);
        if (r < 0)
                return -errno;

        if (r > 0) {
                /* Gotcha, it's a traditional IPv4 address */
                addr->in.sin_family = AF_INET;
                addr->in.sin_port = htobe16(port);
                *addr_len = sizeof(struct sockaddr_in);
        } else {
                unsigned idx;

                if (strlen(s) > IF_NAMESIZE-1)
                        return -EINVAL;

                /* Uh, our last resort, an interface name */
                idx = if_nametoindex(s);
                if (idx == 0)
                        return -EINVAL;

                addr->in6.sin6_family = AF_INET6;
                addr->in6.sin6_port = htobe16(port);
                addr->in6.sin6_scope_id = idx;
                addr->in6.sin6_addr = in6addr_any;
                *addr_len = sizeof(struct sockaddr_in6);
        }

        return 0;
}


int parse_sockaddr(const char *s,
                   union sockaddr_union *addr, unsigned *addr_len) {

        char *e, *n;
        unsigned u;
        int r;

        if (*s == '[') {
                /* IPv6 in [x:.....:z]:p notation */

                e = strchr(s+1, ']');
                if (!e)
                        return -EINVAL;

                n = strndupa(s+1, e-s-1);

                errno = 0;
                if (inet_pton(AF_INET6, n, &addr->in6.sin6_addr) <= 0)
                        return errno > 0 ? -errno : -EINVAL;

                e++;
                if (*e) {
                        if (*e != ':')
                                return -EINVAL;

                        e++;
                        r = safe_atou(e, &u);
                        if (r < 0)
                                return r;

                        if (u <= 0 || u > 0xFFFF)
                                return -EINVAL;

                        addr->in6.sin6_port = htobe16((uint16_t)u);
                }

                addr->in6.sin6_family = AF_INET6;
                *addr_len = sizeof(struct sockaddr_in6);

        } else {
                e = strchr(s, ':');
                if (e) {
                        r = safe_atou(e+1, &u);
                        if (r < 0)
                                return r;

                        if (u <= 0 || u > 0xFFFF)
                                return -EINVAL;

                        n = strndupa(s, e-s);
                        return assign_address(n, u, addr, addr_len);

                } else {
                        r = safe_atou(s, &u);
                        if (r < 0)
                                return assign_address(s, 0, addr, addr_len);

                        /* Just a port */
                        if (u <= 0 || u > 0xFFFF)
                                return -EINVAL;

                        if (socket_ipv6_is_supported()) {
                                addr->in6.sin6_family = AF_INET6;
                                addr->in6.sin6_port = htobe16((uint16_t)u);
                                addr->in6.sin6_addr = in6addr_any;
                                *addr_len = sizeof(struct sockaddr_in6);
                        } else {
                                addr->in.sin_family = AF_INET;
                                addr->in.sin_port = htobe16((uint16_t)u);
                                addr->in.sin_addr.s_addr = INADDR_ANY;
                                *addr_len = sizeof(struct sockaddr_in);
                        }
                }
        }

        return 0;
}
