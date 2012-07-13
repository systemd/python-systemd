from ._journald import sendv
import traceback as _traceback

def _make_line(field, value):
    if isinstance(value, bytes):
        return field.encode('utf-8') + b'=' + value
    else:
        return field + '=' + value

def send(MESSAGE, MESSAGE_ID=None,
         CODE_FILE=None, CODE_LINE=None, CODE_FUNC=None,
         **kwargs):
    """Send a message to journald.

    >>> journald.send('Hello world')
    >>> journald.send('Hello, again, world', FIELD2='Greetings!')
    >>> journald.send('Binary message', BINARY=b'\xde\xad\xbe\xef')

    Value of the MESSAGE argument will be used for the MESSAGE= field.

    MESSAGE_ID can be given to uniquely identify the type of message.

    Other parts of the message can be specified as keyword arguments.

    Both MESSAGE and MESSAGE_ID, if present, must be strings, and will
    be sent as UTF-8 to journald. Other arguments can be bytes, in
    which case they will be sent as-is to journald.

    CODE_LINE, CODE_FILE, and CODE_FUNC can be specified to identify
    the caller. Unless at least on of the three is given, values are
    extracted from the stack frame of the caller of send(). CODE_FILE
    and CODE_FUNC must be strings, CODE_LINE must be an integer.

    Other useful fields include PRIORITY, SYSLOG_FACILITY,
    SYSLOG_IDENTIFIER, SYSLOG_PID.
    """

    args = ['MESSAGE=' + MESSAGE]

    if MESSAGE_ID is not None:
        args.append('MESSAGE_ID=' + MESSAGE_ID)

    if CODE_LINE == CODE_FILE == CODE_FUNC == None:
        CODE_FILE, CODE_LINE, CODE_FUNC = \
            _traceback.extract_stack(limit=2)[0][:3]
    if CODE_FILE is not None:
        args.append('CODE_FILE=' + CODE_FILE)
    if CODE_LINE is not None:
        args.append('CODE_LINE={:d}'.format(CODE_LINE))
    if CODE_FUNC is not None:
        args.append('CODE_FUNC=' + CODE_FUNC)

    args.extend(_make_line(key, val) for key, val in kwargs.items())
    return sendv(*args)
