journald-python
===============

Python module for native access to the journald facilities in recent
versions of systemd. In particular, this capability includes passing
key/value pairs as fields that journald can use for filtering.

Installation
============

On Fedora 17+:

    sudo yum install git python-pip gcc python-devel systemd-devel
    pip-python install git+http://github.com/systemd/python-systemd.git#egg=systemd

Usage
=====

Quick example:

    from systemd import journal
    journal.send('Hello world')
    journal.send('Hello, again, world', FIELD2='Greetings!', FIELD3='Guten tag')
    journal.send('Binary message', BINARY=b'\xde\xad\xbe\xef')

There is one required argument -- the message, and additional fields
can be specified as keyword arguments. Following the journald API, all
names are uppercase.

The journald sendv call can also be accessed directly:

    from systemd import journal
    journal.sendv('MESSAGE=Hello world')
    journal.sendv('MESSAGE=Hello, again, world', 'FIELD2=Greetings!',
                   'FIELD3=Guten tag')
    journal.sendv('MESSAGE=Binary message', b'BINARY=\xde\xad\xbe\xef')

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
    >>> from systemd import journal
    >>> journal.send("Test")
