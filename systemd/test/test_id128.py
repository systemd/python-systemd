import contextlib
import errno
import uuid
import pytest

from systemd import id128

@contextlib.contextmanager
def skip_oserror(code):
    try:
        yield
    except (OSError, IOError) as e:
        if e.errno == code:
            pytest.skip()
        raise


def test_randomize():
    u1 = id128.randomize()
    u2 = id128.randomize()
    assert u1 != u2

def test_get_machine():
    u1 = id128.get_machine()
    u2 = id128.get_machine()
    assert u1 == u2

def test_get_machine_app_specific():
    a1 = uuid.uuid1()
    a2 = uuid.uuid1()

    with skip_oserror(errno.ENOSYS):
        u1 = id128.get_machine_app_specific(a1)

    u2 = id128.get_machine_app_specific(a2)
    u3 = id128.get_machine_app_specific(a1)
    u4 = id128.get_machine_app_specific(a2)

    assert u1 != u2
    assert u1 == u3
    assert u2 == u4

def test_get_boot():
    u1 = id128.get_boot()
    u2 = id128.get_boot()
    assert u1 == u2
