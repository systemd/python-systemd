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
    journald.send('MESSAGE=Hello world')
    journald.send('MESSAGE=Hello, again, world', 'FIELD2=Greetings!', 'FIELD3=Guten tag')
    journald.send('ARBITRARY=anything', 'FIELD3=Greetings!')

Notes:

 * Each argument must be in the form of a KEY=value pair,
   environmental variable style.
 * Unlike the native C version of journald's sd_journal_send(),
   printf-style substitution is not supported. Perform any
   substitution using Python's % operator or .format() capabilities
   first.
 * The base message is usually sent in the form MESSAGE=hello. The
   MESSAGE field is, however, not required.
 * Invalid or zero arguments results in nothing recorded in journald.

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
