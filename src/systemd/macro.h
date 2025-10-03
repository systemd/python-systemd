/*-*- Mode: C; c-basic-offset: 8; indent-tabs-mode: nil -*-*/

#pragma once

/***

  Copyright 2010 Lennart Poettering

  python-systemd is free software; you can redistribute it and/or modify it
  under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  python-systemd is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with python-systemd; If not, see <http://www.gnu.org/licenses/>.
***/

#define DISABLE_WARNING_MISSING_PROTOTYPES                              \
        _Pragma("GCC diagnostic push");                                 \
        _Pragma("GCC diagnostic ignored \"-Wmissing-prototypes\"")

#define REENABLE_WARNING                                                \
        _Pragma("GCC diagnostic pop")

#define DEFINE_TRIVIAL_CLEANUP_FUNC(type, func)                 \
        static inline void func##p(type *p) {                   \
                if (*p)                                         \
                        func(*p);                               \
        }                                                       \
        struct __useless_struct_to_allow_trailing_semicolon__

#define new0(t, n) ((t*) calloc((n), sizeof(t)))
#define alloca0(n)                                      \
        ({                                              \
                char *_new_;                            \
                size_t _len_ = n;                       \
                _new_ = alloca(_len_);                  \
                (void *) memset(_new_, 0, _len_);       \
        })

#define _cleanup_(x) __attribute__((cleanup(x)))

static inline void freep(void *p) {
        free(*(void**) p);
}

#define _cleanup_free_ _cleanup_(freep)

#if defined(static_assert)
#  define assert_cc(expr)                               \
 static_assert(expr, #expr)
#else
#  define assert_cc(expr)
#endif
