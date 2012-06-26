#include <Python.h>
#include <systemd/sd-journal.h>

#ifndef journaldpython
#define journaldpython

static PyObject *
journald_send(PyObject *self, PyObject *args) {
    int argc = PyTuple_Size(args);
    struct iovec *iov = NULL;
    int i;
    
    // Allocate sufficient iovector space for the arguments.
    iov = malloc(argc * sizeof(struct iovec));
    if (!iov) {
        return PyErr_NoMemory();
    }

    // Iterate through the Python arguments and fill the iovector.
    for (i = 0; i < argc; ++i) {
        PyObject *item = PyTuple_GetItem(args, i);
        char * stritem = PyString_AsString(item);
        iov[i].iov_base = stritem;
        iov[i].iov_len = strlen(stritem);
    }
  
    sd_journal_sendv(iov, argc);
    //sd_journal_send("MESSAGE=foobar", "VALUE=%i", 7, NULL);

    //const char *command;
    //int sts;

    //if (!PyArg_ParseTuple(args, "s", &command))
    //    return NULL;
    //sts = system(command);
    
    //return Py_BuildValue("i", sts);
    //sd_journal_print(1, "Testing message: %s. ANOTHERFIELD=one", "arg1", NULL);
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

#endif
