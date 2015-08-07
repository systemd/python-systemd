import sys
import os
import posix
from systemd.daemon import _is_fifo, is_fifo

import pytest

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
