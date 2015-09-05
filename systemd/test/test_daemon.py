import sys
import os
import posix
from systemd.daemon import _is_fifo, is_fifo, listen_fds, booted

import pytest

def test_booted():
    if os.path.exists('/run/systemd'):
        # assume we are running under systemd
        assert booted()
    else:
        # don't assume anything
        assert booted() in {False, True}

def test__is_fifo(tmpdir):
    path = tmpdir.join('test.fifo').strpath
    posix.mkfifo(path)
    fd = os.open(path, os.O_RDONLY|os.O_NONBLOCK)

    assert _is_fifo(fd, None)
    assert _is_fifo(fd, path)

def test__is_fifo_file(tmpdir):
    file = tmpdir.join('test.fifo')
    file.write('boo')
    path = file.strpath
    fd = os.open(path, os.O_RDONLY|os.O_NONBLOCK)

    assert not _is_fifo(fd, None)
    assert not _is_fifo(fd, path)

def test__is_fifo_bad_fd(tmpdir):
    path = tmpdir.join('test.fifo').strpath

    with pytest.raises(OSError):
        assert not _is_fifo(-1, None)

    with pytest.raises(OSError):
        assert not _is_fifo(-1, path)

def test_is_fifo(tmpdir):
    path = tmpdir.join('test.fifo').strpath
    posix.mkfifo(path)
    fd = os.open(path, os.O_RDONLY|os.O_NONBLOCK)
    file = os.fdopen(fd, 'r')

    assert is_fifo(file, None)
    assert is_fifo(file, path)
    assert is_fifo(fd, None)
    assert is_fifo(fd, path)

def test_is_fifo_file(tmpdir):
    file = tmpdir.join('test.fifo')
    file.write('boo')
    path = file.strpath
    fd = os.open(path, os.O_RDONLY|os.O_NONBLOCK)
    file = os.fdopen(fd, 'r')

    assert not is_fifo(file, None)
    assert not is_fifo(file, path)
    assert not is_fifo(fd, None)
    assert not is_fifo(fd, path)

def test_is_fifo_bad_fd(tmpdir):
    path = tmpdir.join('test.fifo').strpath

    with pytest.raises(OSError):
        assert not is_fifo(-1, None)

    with pytest.raises(OSError):
        assert not is_fifo(-1, path)

def test_listen_fds_no_fds():
    # make sure we have no fds to listen to
    os.unsetenv('LISTEN_FDS')
    os.unsetenv('LISTEN_PID')

    assert listen_fds() == []
    assert listen_fds(True) == []
    assert listen_fds(False) == []

def test_listen_fds():
    os.environ['LISTEN_FDS'] = '3'
    os.environ['LISTEN_PID'] = str(os.getpid())

    assert listen_fds(False) == [3, 4, 5]
    assert listen_fds(True) == [3, 4, 5]
    assert listen_fds() == []

def test_listen_fds_default_unset():
    os.environ['LISTEN_FDS'] = '1'
    os.environ['LISTEN_PID'] = str(os.getpid())

    assert listen_fds(False) == [3]
    assert listen_fds() == [3]
    assert listen_fds() == []
