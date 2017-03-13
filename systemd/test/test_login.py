from __future__ import print_function
import select
import contextlib
import errno

from systemd import login

import pytest

@contextlib.contextmanager
def skip_oserror(code):
    try:
        yield
    except (OSError, IOError) as e:
        if e.errno == code:
            pytest.skip()
        raise

def test_seats():
    # just check that we get some sequence back
    with skip_oserror(errno.ENOENT):
        seats = login.seats()
        assert len(seats) >= 0

def test_sessions():
    with skip_oserror(errno.ENOENT):
        sessions = login.sessions()
        assert len(sessions) >= 0

def test_machine_names():
    with skip_oserror(errno.ENOENT):
        machine_names = login.machine_names()
        assert len(machine_names) >= 0

def test_uids():
    with skip_oserror(errno.ENOENT):
        uids = login.uids()
        assert len(uids) >= 0

def test_monitor():
    p = select.poll()

    with skip_oserror(errno.ENOENT):
        m = login.Monitor("machine")
        p.register(m, m.get_events())
        login.machine_names()
        p.poll(1)
        login.machine_names()
