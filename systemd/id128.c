/*-*- Mode: C; c-basic-offset: 8; indent-tabs-mode: nil -*-*/

/***

  Copyright 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>

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

#include <Python.h>

/* Our include is first, so that our defines are replaced by the ones
 * from the system header. If the system header has the same definitions
 * (or does not have them at all), this replacement is silent. If the
 * system header has a different definition, we get a warning. A warning
 * means that the system headers changed incompatibly, and we should update
 * our definition.
 */
#include "id128-defines.h"
#include <systemd/sd-messages.h>

#include "pyutil.h"
#include "macro.h"

#define HAVE_SD_ID128_GET_MACHINE_APP_SPECIFIC (LIBSYSTEMD_VERSION >= 240)

PyDoc_STRVAR(module__doc__,
             "Python interface to the libsystemd-id128 library.\n\n"
             "Provides SD_MESSAGE_* constants and functions to query and generate\n"
             "128-bit unique identifiers."
);

PyDoc_STRVAR(randomize__doc__,
             "randomize() -> UUID\n\n"
             "Return a new random 128-bit unique identifier.\n"
             "Wraps sd_id128_randomize(3)."
);

PyDoc_STRVAR(get_machine__doc__,
             "get_machine() -> UUID\n\n"
             "Return a 128-bit unique identifier for this machine.\n"
             "Wraps sd_id128_get_machine(3)."
);

PyDoc_STRVAR(get_machine_app_specific__doc__,
             "get_machine_app_specific(UUID) -> UUID\n\n"
             "Return a 128-bit unique identifier for this application and machine.\n"
             "Wraps sd_id128_get_machine_app_specific(3)."
);

PyDoc_STRVAR(get_boot__doc__,
             "get_boot() -> UUID\n\n"
             "Return a 128-bit unique identifier for this boot.\n"
             "Wraps sd_id128_get_boot(3)."
);

static PyObject* make_uuid(sd_id128_t id) {
        _cleanup_Py_DECREF_ PyObject
                *uuid = NULL, *UUID = NULL, *bytes = NULL,
                *args = NULL, *kwargs = NULL;

        uuid = PyImport_ImportModule("uuid");
        if (!uuid)
                return NULL;

        UUID = PyObject_GetAttrString(uuid, "UUID");
        bytes = PyBytes_FromStringAndSize((const char*) &id.bytes, sizeof(id.bytes));
        args = Py_BuildValue("()");
        kwargs = PyDict_New();
        if (!UUID || !bytes || !args || !kwargs)
                return NULL;

        if (PyDict_SetItemString(kwargs, "bytes", bytes) < 0)
                return NULL;

        return PyObject_Call(UUID, args, kwargs);
}

#define helper(name)                                                    \
        static PyObject *name(PyObject *self, PyObject *args) {         \
                sd_id128_t id;                                          \
                int r;                                                  \
                                                                        \
                assert(!args);                                          \
                                                                        \
                r = sd_id128_##name(&id);                               \
                if (r < 0) {                                            \
                        errno = -r;                                     \
                        return PyErr_SetFromErrno(PyExc_IOError);       \
                }                                                       \
                                                                        \
                return make_uuid(id);                                   \
        }

helper(randomize)
helper(get_machine)
helper(get_boot)

static PyObject *get_machine_app_specific(PyObject *self, PyObject *args) {
        _cleanup_Py_DECREF_ PyObject *uuid_bytes = NULL;

        uuid_bytes = PyObject_GetAttrString(args, "bytes");
        if (!uuid_bytes)
                return NULL;

#if HAVE_SD_ID128_GET_MACHINE_APP_SPECIFIC
        Py_buffer buffer;
        sd_id128_t app_id;
        int r;

        r = PyObject_GetBuffer(uuid_bytes, &buffer, 0);
        if (r == -1)
                return NULL;

        if (buffer.len != sizeof(sd_id128_t)) {
                PyBuffer_Release(&buffer);
                return NULL;
        }

        r = sd_id128_get_machine_app_specific(*(sd_id128_t*)buffer.buf, &app_id);
        PyBuffer_Release(&buffer);
        if (r < 0) {
                errno = -r;
                return PyErr_SetFromErrno(PyExc_IOError);
        }

        return make_uuid(app_id);

#else
        set_error(-ENOSYS, NULL, "Compiled without support for sd_id128_get_machine_app_specific");
        return NULL;
#endif
}

static PyMethodDef methods[] = {
        { "randomize", randomize, METH_NOARGS, randomize__doc__},
        { "get_machine", get_machine, METH_NOARGS, get_machine__doc__},
        { "get_machine_app_specific", get_machine_app_specific, METH_O, get_machine_app_specific__doc__},
        { "get_boot", get_boot, METH_NOARGS, get_boot__doc__},
        {}        /* Sentinel */
};

static int add_id(PyObject *module, const char* name, sd_id128_t id) {
        PyObject *obj;

        obj = make_uuid(id);
        if (!obj)
                return -1;

        return PyModule_AddObject(module, name, obj);
}

#if PY_MAJOR_VERSION < 3

DISABLE_WARNING_MISSING_PROTOTYPES;
PyMODINIT_FUNC initid128(void) {
        PyObject *m;

        m = Py_InitModule3("id128", methods, module__doc__);
        if (!m)
                return;

        /* a series of lines like 'add_id() ;' follow */
#define JOINER ;
#include "id128-constants.h"
#undef JOINER
        PyModule_AddStringConstant(m, "__version__", PACKAGE_VERSION);
}
REENABLE_WARNING;

#else

static struct PyModuleDef module = {
        PyModuleDef_HEAD_INIT,
        .m_name = "id128", /* name of module */
        .m_doc = module__doc__, /* module documentation */
        .m_size = -1, /* size of per-interpreter state of the module */
        .m_methods = methods,
};

DISABLE_WARNING_MISSING_PROTOTYPES;
PyMODINIT_FUNC PyInit_id128(void) {
        PyObject *m;

        m = PyModule_Create(&module);
        if (!m)
                return NULL;

        if ( /* a series of lines like 'add_id() ||' follow */
#define JOINER ||
#include "id128-constants.h"
#undef JOINER
            PyModule_AddStringConstant(m, "__version__", PACKAGE_VERSION)) {
                Py_DECREF(m);
                return NULL;
        }

        return m;
}
REENABLE_WARNING;

#endif
