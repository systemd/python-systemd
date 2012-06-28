from ._journald import sendv

def send(MESSAGE, MESSAGE_ID=None, **kwargs):
    """Send a message to journald.

    >>> journald.send('Hello world')
    >>> journald.send('Hello, again, world', FIELD2='Greetings!')
    >>> journald.send('Binary message', BINARY='\xde\xad\xbe\xef')

    Value of the MESSAGE argument will be used for the MESSAGE= field.

    MESSAGE_ID can be given to uniquely identify the type of message.

    Other parts of the message can be specified as keyword arguments.

    CODE_LINE, CODE_FILE, and CODE_FUNC can be specified to identify
    the caller. Unless at least on of the three is given, values are
    extracted from the stack frame of the caller of send(). CODE_FILE
    and CODE_FUNC should be strings, CODE_LINE should be an integer.

    Other useful fields include PRIORITY, SYSLOG_FACILITY,
    SYSLOG_IDENTIFIER, SYSLOG_PID.
    """

    args = ['MESSAGE=' + MESSAGE]
    if MESSAGE_ID is not None:
        args.append('MESSAGE_ID=' + MESSAGE_ID)
    for key, val in kwargs.items():
        args.append(key + '=' + val)
    return sendv(*args)
