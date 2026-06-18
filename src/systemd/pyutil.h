/* SPDX-License-Identifier: LGPL-2.1-or-later */

#pragma once

#define PY_SSIZE_T_CLEAN
/* Work around bug in Python.h:
 * it tries to redefine defines already defined by /usr/include/features.h,
 * without calling #undef first, causing a warning to be emitted.
 * (https://github.com/python/cpython/issues/61322). */
#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#  include <Python.h>
#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#define _XOPEN_SOURCE  800
#define _POSIX_C_SOURCE 202405L

void cleanup_Py_DECREFp(PyObject **p);
PyObject* absolute_timeout(uint64_t t);
int set_error(int r, const char* path, const char* invalid_message);

int Unicode_FSConverter(PyObject* obj, void *_result);

#define _cleanup_Py_DECREF_ _cleanup_(cleanup_Py_DECREFp)
