python-systemd
===============

Python module for native access to the systemd facilities. Functionality
is separated into a number of modules:
- `systemd.journal` supports sending of structured messages to the journal
  and reading journal files,
- `systemd.daemon` wraps parts of `libsystemd` useful for writing daemons
  and socket activation,
- `systemd.id128` provides functions for querying machine and boot identifiers
  and a lists of message identifiers provided by systemd,
- `systemd.login` wraps parts of `libsystemd` used to query logged in users
  and available seats and machines.

Installation
============

This module should be packaged for almost all Linux distributions. Use

On Fedora:

    dnf install python3-systemd

On Debian/Ubuntu/Mint:

    apt update
    apt install python3-systemd

On openSUSE and SLE:

    zypper in python3-systemd

On Arch:

    pacman -Sy python-systemd

To build from source
--------------------

On CentOS, RHEL, and Fedora with Python 2:

    dnf install git python-pip gcc python-devel systemd-devel
    pip install 'git+https://github.com/systemd/python-systemd.git#egg=systemd-python'

On Fedora with Python 3:

    dnf install git python3-pip gcc python3-devel systemd-devel
    pip3 install 'git+https://github.com/systemd/python-systemd.git#egg=systemd-python'

On Debian or Ubuntu with Python 2:

    apt install libsystemd-{journal,daemon,login,id128}-dev gcc python-dev pkg-config

On Debian or Ubuntu with Python 3:

    apt install libsystemd-{journal,daemon,login,id128}-dev gcc python3-dev pkg-config

The project is also available on pypi as `systemd-python`.

Usage
=====

Quick example:

    from systemd import journal
    journal.send('Hello world')
    journal.send('Hello, again, world', FIELD2='Greetings!', FIELD3='Guten tag')
    journal.send('Binary message', BINARY=b'\xde\xad\xbe\xef')

There is one required argument — the message, and additional fields
can be specified as keyword arguments. Following the journald API, all
names are uppercase.

The journald sendv call can also be accessed directly:

    from systemd import journal
    journal.sendv('MESSAGE=Hello world')
    journal.sendv('MESSAGE=Hello, again, world', 'FIELD2=Greetings!',
                   'FIELD3=Guten tag')
    journal.sendv('MESSAGE=Binary message', b'BINARY=\xde\xad\xbe\xef')

The two examples should give the same results in the log.

Reading from the journal is often similar to using the `journalctl` utility.

Show all entries since 20 minutes ago (`journalctl --since "20 minutes ago"`):

    from systemd import journal
    from datetime import datetime, timedelta
    j = journal.Reader()
    j.seek_realtime(datetime.now() - timedelta(minutes=20))
    for entry in j:
        print(entry['MESSAGE'])

Show entries between two timestamps (`journalctl --since "50 minutes ago" --until "10 minutes ago"`):

    from systemd import journal
    from datetime import datetime, timedelta
    j = journal.Reader()
    since = datetime.now() - timedelta(minutes=50)
    until = datetime.now() - timedelta(minutes=10)
    j.seek_realtime(since)
    for entry in j:
      if entry['__REALTIME_TIMESTAMP'] > until:
        break
      print(entry['MESSAGE'])

Show explanations of log messages alongside entries (`journalctl -x`):

    from systemd import journal
    j = journal.Reader()
    for entry in j:
        print("MESSAGE: ", entry['MESSAGE'])
        try:
            print("CATALOG: ", j.get_catalog())
        except:
            pass

Show entries by a specific executable (`journalctl /usr/bin/vim`):

    from systemd import journal
    j = journal.Reader()
    j.add_match('_EXE=/usr/bin/vim')
    for entry in j:
        print(entry['MESSAGE'])

 - Note: matches can be added from many different fields, for example
   entries from a specific process ID can be matched with the `_PID`
   field, and entries from a specific unit (ie. `journalctl -u
   systemd-udevd.service`) can be matched with `_SYSTEMD_UNIT`.
   See all fields available at the
   [systemd.journal-fields docs](https://www.freedesktop.org/software/systemd/man/systemd.journal-fields.html).

Show kernel ring buffer (`journalctl -k`):

    from systemd import journal
    j = journal.Reader()
    j.add_match('_TRANSPORT=kernel')
    for entry in j:
        print(entry['MESSAGE'])

Read entries in reverse (`journalctl _EXE=/usr/bin/vim -r`):
  
    from systemd import journal
    class ReverseReader(journal.Reader):
        def __next__(self):
            ans = self.get_previous()
            if ans:
                return ans
            raise StopIteration()

    j = ReverseReader()
    j.add_match('_EXE=/usr/bin/vim')
    j.seek_tail()
    for entry in j:
      print(entry['MESSAGE'])


Notes
-----

* Unlike the native C version of journald's `sd_journal_send()`,
  printf-style substitution is not supported. Perform any substitution
  using Python's f-strings first (or `.format()` or the `%` operator).
* A `ValueError` is raised if `sd_journald_sendv()` results in an
  error. This might happen if there are no arguments or one of them is
  invalid.

A handler class for the Python logging framework is also provided:

    import logging
    from systemd import journal
    logger = logging.getLogger('custom_logger_name')
    logger.addHandler(journal.JournalHandler(SYSLOG_IDENTIFIER='custom_unit_name'))
    logger.warning("Some message: %s", 'detail')

`libsystemd` version compatibility
----------------------------------

This module may be compiled against any version of `libsystemd`. At
compilation time, any functionality that is not available in that
version is disabled, and the resulting binary module will depend on
symbols that were available at compilation time. This means that the
resulting binary module is compatible with that or any later version
of `libsystemd`. To obtain maximum possible functionality, this module
must be compile against suitably recent libsystemd.

Documentation
=============

Online documentation can be found at [freedesktop.org](https://www.freedesktop.org/software/systemd/python-systemd/)

To build it locally run:

    make sphinx-html

Or use any other builder, see `man sphinx-build` for a list. The compiled docs will be e.g. in `docs/html`.

Viewing Output
==============

Quick way to view output with all fields as it comes in:

    sudo journalctl -f --output=json

Test Builds (for Development)
=============================

    python setup.py build_ext -i
    python
    >>> from systemd import journal
    >>> journal.send("Test")

[![Build Status](https://semaphoreci.com/api/v1/projects/42d43c62-f6e5-4fd5-a93a-2b165e6be575/530946/badge.svg)](https://semaphoreci.com/zbyszek/python-systemd)
