`systemd.login` module
=======================

.. automodule:: systemd.login
   :members:

.. autoclass:: Monitor
   :undoc-members:
   :inherited-members:

Example: polling for events
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example shows that session/uid/seat/machine events can be waited
for (using e.g. `poll`). This makes it easy to integrate Monitor in an
external event loop:

  >>> import select
  >>> from systemd import login
  >>> m = login.Monitor("machine")        # doctest: +SKIP
  >>> p = select.poll()
  >>> p.register(m, m.get_events())       # doctest: +SKIP
  >>> login.machine_names()               # doctest: +SKIP
  []
  >>> p.poll()                            # doctest: +SKIP
  [(3, 1)]
  >>> login.machine_names()               # doctest: +SKIP
  ['fedora-25']
