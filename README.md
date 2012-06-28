journald-python
===============

Python module for native access to the journald facilities in recent
versions of systemd. In particular, this capability includes passing
key/value pairs as fields that journald can use for filtering.

Installation
============

On Fedora 17+:

    sudo yum install git python-pip gcc python-devel systemd-devel
    pip-python install git+http://github.com/davidstrauss/journald-python.git#egg=journald

Usage
=====

Quick example:

    import journald
    journald.send('Hello world')
    journald.send('Hello, again, world', FIELD2='Greetings!', FIELD3='Guten tag')
    journald.send('Binary message', BINARY='\xde\xad\xbe\xef')

There is one required argument -- the message, and additional fields
can be specified as keyword arguments. Following the journald API, all
names are uppercase.

The journald sendv call can also be accessed directly:

    import journald
    journald.sendv('MESSAGE=Hello world')
    journald.sendv('MESSAGE=Hello, again, world', 'FIELD2=Greetings!',
                   'FIELD3=Guten tag')
    journald.sendv('MESSAGE=Binary message', 'BINARY=\xde\xad\xbe\xef')

The two examples should give the same results in the log.

Notes:

 * Unlike the native C version of journald's sd_journal_send(),
   printf-style substitution is not supported. Perform any
   substitution using Python's % operator or .format() capabilities
   first.
 * The base message is usually sent in the form MESSAGE=hello. The
   MESSAGE field is, however, not required.
 * A ValueError is thrown is thrown if sd_journald_sendv() results in
   an error. This might happen if there are no arguments or one of them
   is invalid.

Viewing Output
==============

Quick way to view output with all fields as it comes in:

    sudo journalctl -f --output=json

Test Builds (for Development)
=============================

    python setup.py build
    cd builds/lib.*
    python
    >>> import journald
    >>> journald.send("Test")
