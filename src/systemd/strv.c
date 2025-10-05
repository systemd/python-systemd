/* SPDX-License-Identifier: LGPL-2.1-or-later */

#include <stdlib.h>

void strv_clear(char **l) {
        char **k;

        if (!l)
                return;

        for (k = l; *k; k++)
                free(*k);

        *l = NULL;
}

char **strv_free(char **l) {
        strv_clear(l);
        free(l);
        return NULL;
}
