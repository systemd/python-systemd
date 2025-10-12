/* SPDX-License-Identifier: LGPL-2.1-or-later */

#pragma once

#include <stdlib.h>

#define DISABLE_WARNING_MISSING_PROTOTYPES                              \
        _Pragma("GCC diagnostic push");                                 \
        _Pragma("GCC diagnostic ignored \"-Wmissing-prototypes\"")

#define DISABLE_WARNING_CAST_FUNCTION_TYPE                              \
        _Pragma("GCC diagnostic push");                                 \
        _Pragma("GCC diagnostic ignored \"-Wcast-function-type\"")

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

#define _unused_ __attribute__((__unused__))
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
