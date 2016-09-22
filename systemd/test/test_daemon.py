import sys
import os
import posix
import socket
import contextlib
import errno
from systemd.daemon import (booted,
                            is_fifo, _is_fifo,
                            is_socket, _is_socket,
                            is_socket_inet, _is_socket_inet,
                            is_socket_unix, _is_socket_unix,
                            is_mq, _is_mq,
                            listen_fds,
                            notify)

import pytest

@contextlib.contextmanager
def skip_enosys():
    try:
        yield
    except OSError as e:
        if e.errno == errno.ENOSYS:
            pytest.skip()
        raise

@contextlib.contextmanager
def closing_socketpair(family):
    pair = socket.socketpair(family)
    try:
        yield pair
    finally:
        pair[0].close()
        pair[1].close()


def test_booted():
    if os.path.exists('/run/systemd/system'):
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

def is_mq_wrapper(arg):
    try:
        return is_mq(arg)
    except OSError as error:
        # systemd < 227 compatibility
        assert error.errno == errno.EBADF
        return False

def _is_mq_wrapper(arg):
    try:
        return _is_mq(arg)
    except OSError as error:
        # systemd < 227 compatibility
        assert error.errno == errno.EBADF
        return False

def test_no_mismatch():
    with closing_socketpair(socket.AF_UNIX) as pair:
        for sock in pair:
            assert not is_fifo(sock)
            assert not is_mq_wrapper(sock)
            assert not is_socket_inet(sock)

            fd = sock.fileno()
            assert not is_fifo(fd)
            assert not is_mq_wrapper(fd)
            assert not is_socket_inet(fd)

            assert not _is_fifo(fd)
            assert not _is_mq_wrapper(fd)
            assert not _is_socket_inet(fd)

def test_is_socket():
    with closing_socketpair(socket.AF_UNIX) as pair:
        for sock in pair:
            for arg in (sock, sock.fileno()):
                assert is_socket(arg)
                assert is_socket(arg, socket.AF_UNIX)
                assert not is_socket(arg, socket.AF_INET)
                assert is_socket(arg, socket.AF_UNIX, socket.SOCK_STREAM)
                assert not is_socket(arg, socket.AF_INET, socket.SOCK_DGRAM)

                assert is_socket(sock)
                assert is_socket(arg, socket.AF_UNIX)
                assert not is_socket(arg, socket.AF_INET)
                assert is_socket(arg, socket.AF_UNIX, socket.SOCK_STREAM)
                assert not is_socket(arg, socket.AF_INET, socket.SOCK_DGRAM)

def test__is_socket():
    with closing_socketpair(socket.AF_UNIX) as pair:
        for sock in pair:
            fd = sock.fileno()
            assert _is_socket(fd)
            assert _is_socket(fd, socket.AF_UNIX)
            assert not _is_socket(fd, socket.AF_INET)
            assert _is_socket(fd, socket.AF_UNIX, socket.SOCK_STREAM)
            assert not _is_socket(fd, socket.AF_INET, socket.SOCK_DGRAM)

            assert _is_socket(fd)
            assert _is_socket(fd, socket.AF_UNIX)
            assert not _is_socket(fd, socket.AF_INET)
            assert _is_socket(fd, socket.AF_UNIX, socket.SOCK_STREAM)
            assert not _is_socket(fd, socket.AF_INET, socket.SOCK_DGRAM)

def test_is_socket_unix():
    with closing_socketpair(socket.AF_UNIX) as pair:
        for sock in pair:
            for arg in (sock, sock.fileno()):
                assert is_socket_unix(arg)
                assert not is_socket_unix(arg, path="/no/such/path")
                assert is_socket_unix(arg, socket.SOCK_STREAM)
                assert not is_socket_unix(arg, socket.SOCK_DGRAM)

def test__is_socket_unix():
    with closing_socketpair(socket.AF_UNIX) as pair:
        for sock in pair:
            fd = sock.fileno()
            assert _is_socket_unix(fd)
            assert not _is_socket_unix(fd, 0, -1, "/no/such/path")
            assert _is_socket_unix(fd, socket.SOCK_STREAM)
            assert not _is_socket_unix(fd, socket.SOCK_DGRAM)

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

def test_notify_no_socket():
    assert notify('READY=1') == False
    with skip_enosys():
        assert notify('FDSTORE=1', fds=[]) == False
    assert notify('FDSTORE=1', fds=[1,2]) == False
    assert notify('FDSTORE=1', pid=os.getpid()) == False
    assert notify('FDSTORE=1', pid=os.getpid(), fds=(1,)) == False

if sys.version_info >= (3,):
    connection_error = ConnectionRefusedError
else:
    connection_error = OSError

def test_notify_bad_socket():
    os.environ['NOTIFY_SOCKET'] = '/dev/null'

    with pytest.raises(connection_error):
        notify('READY=1')
    with pytest.raises(connection_error):
        with skip_enosys():
            notify('FDSTORE=1', fds=[])
    with pytest.raises(connection_error):
        notify('FDSTORE=1', fds=[1,2])
    with pytest.raises(connection_error):
        notify('FDSTORE=1', pid=os.getpid())
    with pytest.raises(connection_error):
        notify('FDSTORE=1', pid=os.getpid(), fds=(1,))

def test_notify_with_socket(tmpdir):
    path = tmpdir.join('socket').strpath
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind(path)
    # SO_PASSCRED is not defined in python2.7
    SO_PASSCRED = getattr(socket, 'SO_PASSCRED', 16)
    sock.setsockopt(socket.SOL_SOCKET, SO_PASSCRED, 1)
    os.environ['NOTIFY_SOCKET'] = path

    assert notify('READY=1') == True
    with skip_enosys():
        assert notify('FDSTORE=1', fds=[]) == True
    assert notify('FDSTORE=1', fds=[1,2]) == True
    assert notify('FDSTORE=1', pid=os.getpid()) == True
    assert notify('FDSTORE=1', pid=os.getpid(), fds=(1,)) == True
