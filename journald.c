#include <Python.h>
#include <systemd/sd-journal.h>

#ifndef journaldpython
#define journaldpython

static PyObject *
journald_send(PyObject *self, PyObject *args)
{
    //const char *command;
    //int sts;

    //if (!PyArg_ParseTuple(args, "s", &command))
    //    return NULL;
    //sts = system(command);
    //return Py_BuildValue("i", sts);
    sd_journal_send("Test message: %s.", "arg1", NULL);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef journaldMethods[] = {
    {"send",  journald_send, METH_VARARGS,
     "Send an entry to journald."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initjournal(void)
{
    (void) Py_InitModule("journald", journaldMethods);
}

#endif
