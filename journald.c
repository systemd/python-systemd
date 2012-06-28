#include <Python.h>
#include <systemd/sd-journal.h>

static PyObject *
journald_send(PyObject *self, PyObject *args) {
    struct iovec *iov = NULL;
    int argc = PyTuple_Size(args);
    int i;

    // Allocate sufficient iovector space for the arguments.
    iov = malloc(argc * sizeof(struct iovec));
    if (!iov) {
        return PyErr_NoMemory();
    }

    // Iterate through the Python arguments and fill the iovector.
    for (i = 0; i < argc; ++i) {
        PyObject *item = PyTuple_GetItem(args, i);
        char *stritem;
        Py_ssize_t length;
        if (PyString_AsStringAndSize(item, &stritem, &length)) {
            // PyString_AsS&S has already raised TypeError at this
            // point. We can just free iov and return NULL.
            free(iov);
            return NULL;
        }
        iov[i].iov_base = stritem;
        iov[i].iov_len = length;
    }

    // Send the iovector to journald.
    sd_journal_sendv(iov, argc);

    // Free the iovector. The actual strings
    // are already managed by Python.
    free(iov);

    // End with success.
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef journaldMethods[] = {
    {"send",  journald_send, METH_VARARGS,
     "Send an entry to journald."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initjournald(void)
{
    (void) Py_InitModule("journald", journaldMethods);
}
