#include <Python.h>
#include <systemd/sd-journal.h>

static PyObject *
journald_send(PyObject *self, PyObject *args) {
    struct iovec *iov = NULL;
    int argc = PyTuple_Size(args);
    int i, r;
    PyObject *ret = NULL;

#if PY_MAJOR_VERSION >= 3
    PyObject **ascii = calloc(argc, sizeof(PyObject*));
    if (!ascii) {
        ret = PyErr_NoMemory();
        goto out1;
    }
#endif

    // Allocate sufficient iovector space for the arguments.
    iov = malloc(argc * sizeof(struct iovec));
    if (!iov) {
        ret = PyErr_NoMemory();
        goto out;
    }

    // Iterate through the Python arguments and fill the iovector.
    for (i = 0; i < argc; ++i) {
        PyObject *item = PyTuple_GetItem(args, i);
        char *stritem;
        Py_ssize_t length;
#if PY_MAJOR_VERSION < 3
        if (PyString_AsStringAndSize(item, &stritem, &length))
            // PyString_AsS&S has already raised TypeError at this
            // point. We can just free iov and return NULL.
            goto out;
#else
        ascii[i] = PyUnicode_AsASCIIString(item);
        if (ascii[i] == NULL ||
            PyBytes_AsStringAndSize(ascii[i], &stritem, &length))
            goto out;
#endif
        iov[i].iov_base = stritem;
        iov[i].iov_len = length;
    }

    // Clear errno, because sd_journal_sendv will not set it by
    // itself, unless an error occurs in one of the system calls.
    errno = 0;

    // Send the iovector to journald.
    r = sd_journal_sendv(iov, argc);

    if (r) {
        if (errno)
            PyErr_SetFromErrno(PyExc_IOError);
        else
            PyErr_SetString(PyExc_ValueError, "invalid message format");
        goto out;
    }

    // End with success.
    Py_INCREF(Py_None);
    ret = Py_None;

out:
#if PY_MAJOR_VERSION >= 3
    for (i = 0; i < argc; ++i)
        Py_XDECREF(ascii[i]);

    free(ascii);
#endif

out1:
    // Free the iovector. The actual strings
    // are already managed by Python.
    free(iov);

    return ret;
}

static PyMethodDef methods[] = {
    {"send",  journald_send, METH_VARARGS,
     "Send an entry to journald."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

#if PY_MAJOR_VERSION < 3

PyMODINIT_FUNC
initjournald(void)
{
    (void) Py_InitModule("journald", methods);
}

#else

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "journald", /* name of module */
    NULL, /* module documentation, may be NULL */
    0, /* size of per-interpreter state of the module */
    methods
};

PyMODINIT_FUNC
PyInit_journald(void)
{
    return PyModule_Create(&module);
}

#endif
