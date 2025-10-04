/* SPDX-License-Identifier: LGPL-2.1-or-later */

#pragma once

#include <netinet/ip.h>
#include <arpa/inet.h>

union sockaddr_union {
        struct sockaddr sa;
        struct sockaddr_in in;
        struct sockaddr_in6 in6;
};

int safe_atou(const char *s, unsigned *ret_u);
int parse_sockaddr(const char *s,
                   union sockaddr_union *addr, unsigned *addr_len);
