/* SPDX-License-Identifier: LGPL-2.1-or-later */

#pragma once

/***
  Copyright 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>
***/

#ifndef Py_TYPE
/* avoid duplication warnings from errors in Python 2.7 headers */
# include <Python.h>
#endif

void cleanup_Py_DECREFp(PyObject **p);
PyObject* absolute_timeout(uint64_t t);
int set_error(int r, const char* path, const char* invalid_message);

int Unicode_FSConverter(PyObject* obj, void *_result);

#define _cleanup_Py_DECREF_ _cleanup_(cleanup_Py_DECREFp)

# define unicode_FromStringAndSize PyUnicode_FromStringAndSize
# define unicode_FromString PyUnicode_FromString
# define long_FromLong PyLong_FromLong
# define long_FromSize_t PyLong_FromSize_t
# define long_Check PyLong_Check
# define long_AsLong PyLong_AsLong
