/* SPDX-License-Identifier: LGPL-2.1-or-later */

#include <alloca.h>

#define SD_JOURNAL_SUPPRESS_LOCATION
#include "systemd/sd-journal.h"

#include "macro.h"
#include "pyutil.h"

PyDoc_STRVAR(journal_sendv__doc__,
             "sendv('FIELD=value', 'FIELD=value', ...) -> None\n\n"
             "Send an entry to the journal."
);

static PyObject* journal_sendv(PyObject *self _unused_, PyObject *args) {
        PyObject *ret = NULL;
        int r;

        /* Allocate an array for the argument strings */
        int argc = PyTuple_Size(args);
        PyObject **encoded = alloca0(argc * sizeof(PyObject*));

        /* Allocate sufficient iovector space for the arguments. */
        struct iovec *iov = alloca(argc * sizeof(struct iovec));

        /* Iterate through the Python arguments and fill the iovector. */
        for (int i = 0; i < argc; ++i) {
                PyObject *item = PyTuple_GetItem(args, i);
                char *stritem;
                Py_ssize_t length;

                if (PyUnicode_Check(item)) {
                        encoded[i] = PyUnicode_AsEncodedString(item, "utf-8", "strict");
                        if (!encoded[i])
                                goto out;
                        item = encoded[i];
                }
                if (PyBytes_AsStringAndSize(item, &stritem, &length))
                        goto out;

                iov[i].iov_base = stritem;
                iov[i].iov_len = length;
        }

        /* Send the iovector to the journal. */
        r = sd_journal_sendv(iov, argc);
        if (r < 0) {
                errno = -r;
                PyErr_SetFromErrno(PyExc_OSError);
                goto out;
        }

        /* End with success. */
        Py_INCREF(Py_None);
        ret = Py_None;

out:
        for (int i = 0; i < argc; i++)
                Py_XDECREF(encoded[i]);

        return ret;
}

PyDoc_STRVAR(journal_stream_fd__doc__,
             "stream_fd(identifier, priority, level_prefix) -> fd\n\n"
             "Open a stream to journal by calling sd_journal_stream_fd(3)."
);

static PyObject* journal_stream_fd(PyObject *self _unused_, PyObject *args) {
        const char* identifier;
        int priority, level_prefix;
        int fd;

        if (!PyArg_ParseTuple(args, "sii:stream_fd",
                              &identifier, &priority, &level_prefix))
                return NULL;

        fd = sd_journal_stream_fd(identifier, priority, level_prefix);
        if (fd < 0) {
                errno = -fd;
                return PyErr_SetFromErrno(PyExc_OSError);
        }

        return PyLong_FromLong(fd);
}

static PyMethodDef methods[] = {
        { "sendv",     journal_sendv,     METH_VARARGS, journal_sendv__doc__     },
        { "stream_fd", journal_stream_fd, METH_VARARGS, journal_stream_fd__doc__ },
        {}        /* Sentinel */
};

static struct PyModuleDef module = {
        PyModuleDef_HEAD_INIT,
        .m_name = "_journal", /* name of module */
        .m_size = -1, /* size of per-interpreter state of the module */
        .m_methods = methods,
};

DISABLE_WARNING_MISSING_PROTOTYPES;
PyMODINIT_FUNC PyInit__journal(void) {
        PyObject *m;

        m = PyModule_Create(&module);
        if (!m)
                return NULL;

        if (PyModule_AddStringConstant(m, "__version__", PACKAGE_VERSION)) {
                Py_DECREF(m);
                return NULL;
        }

        return m;
}
REENABLE_WARNING;
