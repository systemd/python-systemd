/* SPDX-License-Identifier: LGPL-2.1-or-later */

#include "macro.h"

char **strv_free(char **l);
DEFINE_TRIVIAL_CLEANUP_FUNC(char**, strv_free);
#define _cleanup_strv_free_ _cleanup_(strv_freep)
