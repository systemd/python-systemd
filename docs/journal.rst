`systemd.journal` module
========================

.. automodule:: systemd.journal
   :members: send, sendv, stream, stream_fd
   :undoc-members:

`JournalHandler` class
----------------------

.. autoclass:: JournalHandler

Accessing the Journal
---------------------

.. autoclass:: _Reader
   :undoc-members:
   :inherited-members:

.. autoclass:: Reader
   :undoc-members:
   :inherited-members:

   .. automethod:: __init__

.. autofunction:: _get_catalog
.. autofunction:: get_catalog

.. autoclass:: Monotonic

.. autoattribute:: systemd.journal.DEFAULT_CONVERTERS

Example: polling for journal events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example shows that journal events can be waited for (using
e.g. `poll`). This makes it easy to integrate Reader in an external
event loop:

  >>> import select
  >>> from systemd import journal
  >>> j = journal.Reader()
  >>> j.seek_tail()
  >>> journal.send('testing 1,2,3')   # make sure we have something to read
  >>> j.add_match('MESSAGE=testing 1,2,3')
  >>> p = select.poll()
  >>> p.register(j, j.get_events())
  >>> p.poll()                        # doctest: +SKIP
  [(3, 1)]
  >>> j.get_next()                    # doctest: +SKIP
  {'_AUDIT_LOGINUID': 1000,
   '_CAP_EFFECTIVE': '0',
   '_SELINUX_CONTEXT': 'unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023',
   '_GID': 1000,
   'CODE_LINE': 1,
   '_HOSTNAME': '...',
   '_SYSTEMD_SESSION': 52,
   '_SYSTEMD_OWNER_UID': 1000,
   'MESSAGE': 'testing 1,2,3',
   '__MONOTONIC_TIMESTAMP':
      journal.Monotonic(timestamp=datetime.timedelta(2, 76200, 811585),
                        bootid=UUID('958b7e26-df4c-453a-a0f9-a8406cb508f2')),
   'SYSLOG_IDENTIFIER': 'python3',
   '_UID': 1000,
   '_EXE': '/usr/bin/python3',
   '_PID': 7733,
   '_COMM': '...',
   'CODE_FUNC': '<module>',
   'CODE_FILE': '<doctest journal.rst[4]>',
   '_SOURCE_REALTIME_TIMESTAMP':
       datetime.datetime(2015, 9, 5, 13, 17, 4, 944355),
   '__CURSOR': 's=...',
   '_BOOT_ID': UUID('958b7e26-df4c-453a-a0f9-a8406cb508f2'),
   '_CMDLINE': '/usr/bin/python3 ...',
   '_MACHINE_ID': UUID('263bb31e-3e13-4062-9bdb-f1f4518999d2'),
   '_SYSTEMD_SLICE': 'user-1000.slice',
   '_AUDIT_SESSION': 52,
   '__REALTIME_TIMESTAMP': datetime.datetime(2015, 9, 5, 13, 17, 4, 945110),
   '_SYSTEMD_UNIT': 'session-52.scope',
   '_SYSTEMD_CGROUP': '/user.slice/user-1000.slice/session-52.scope',
   '_TRANSPORT': 'journal'}



Journal access types
~~~~~~~~~~~~~~~~~~~~

.. autoattribute:: systemd.journal.LOCAL_ONLY
.. autoattribute:: systemd.journal.RUNTIME_ONLY
.. autoattribute:: systemd.journal.SYSTEM
.. autoattribute:: systemd.journal.CURRENT_USER
.. autoattribute:: systemd.journal.OS_ROOT

Journal event types
~~~~~~~~~~~~~~~~~~~

.. autoattribute:: systemd.journal.NOP
.. autoattribute:: systemd.journal.APPEND
.. autoattribute:: systemd.journal.INVALIDATE
