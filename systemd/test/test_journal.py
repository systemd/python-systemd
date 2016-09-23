import contextlib
import datetime
import errno
import logging
import os
import time
import uuid

from systemd import journal, id128

import pytest

TEST_MID = uuid.UUID('8441372f8dca4ca98694a6091fd8519f')

@contextlib.contextmanager
def skip_enosys():
    try:
        yield
    except OSError as e:
        if e.errno == errno.ENOSYS:
            pytest.skip()
        raise

@contextlib.contextmanager
def skip_valueerror():
    try:
        yield
    except ValueError:
        pytest.skip()

def test_priorities():
    p = journal.JournalHandler.mapPriority

    assert p(logging.NOTSET)       == journal.LOG_DEBUG
    assert p(logging.DEBUG)        == journal.LOG_DEBUG
    assert p(logging.DEBUG - 1)    == journal.LOG_DEBUG
    assert p(logging.DEBUG + 1)    == journal.LOG_INFO
    assert p(logging.INFO - 1)     == journal.LOG_INFO
    assert p(logging.INFO)         == journal.LOG_INFO
    assert p(logging.INFO + 1)     == journal.LOG_WARNING
    assert p(logging.WARN - 1)     == journal.LOG_WARNING
    assert p(logging.WARN)         == journal.LOG_WARNING
    assert p(logging.WARN + 1)     == journal.LOG_ERR
    assert p(logging.ERROR - 1)    == journal.LOG_ERR
    assert p(logging.ERROR)        == journal.LOG_ERR
    assert p(logging.ERROR + 1)    == journal.LOG_CRIT
    assert p(logging.FATAL)        == journal.LOG_CRIT
    assert p(logging.CRITICAL)     == journal.LOG_CRIT
    assert p(logging.CRITICAL + 1) == journal.LOG_ALERT


def test_journalhandler_init_exception():
    kw = {' X  ':3}
    with pytest.raises(ValueError):
        journal.JournalHandler(**kw)

def test_journalhandler_init():
    kw = {'X':3, 'X3':4}
    journal.JournalHandler(logging.INFO, **kw)

def test_reader_init_flags():
    j1 = journal.Reader()
    j2 = journal.Reader(journal.LOCAL_ONLY)
    j3 = journal.Reader(journal.RUNTIME_ONLY)
    j4 = journal.Reader(journal.SYSTEM_ONLY)
    j5 = journal.Reader(journal.LOCAL_ONLY | journal.RUNTIME_ONLY | journal.SYSTEM_ONLY)
    j6 = journal.Reader(0)

def test_reader_os_root(tmpdir):
    with pytest.raises(ValueError):
        journal.Reader(journal.OS_ROOT)
    with skip_valueerror():
        j1 = journal.Reader(path=tmpdir.strpath,
                            flags=journal.OS_ROOT)
    with skip_valueerror():
        j2 = journal.Reader(path=tmpdir.strpath,
                            flags=journal.OS_ROOT | journal.CURRENT_USER)
    j3 = journal.Reader(path=tmpdir.strpath,
                        flags=journal.OS_ROOT | journal.SYSTEM_ONLY)

def test_reader_init_path(tmpdir):
    j1 = journal.Reader(path=tmpdir.strpath)
    journal.Reader(0, path=tmpdir.strpath)

    j2 = journal.Reader(path=tmpdir.strpath)
    journal.Reader(path=tmpdir.strpath)

def test_reader_init_path_invalid_fd():
    with pytest.raises(OSError):
        journal.Reader(0, path=-1)

def test_reader_init_path_nondirectory_fd():
    with pytest.raises(OSError):
        journal.Reader(0, path=0)

def test_reader_init_path_fd(tmpdir):
    fd = os.open(tmpdir.strpath, os.O_RDONLY)

    with skip_enosys():
        j1 = journal.Reader(path=fd)
    assert list(j1) == []

    with skip_valueerror():
        j2 = journal.Reader(journal.SYSTEM, path=fd)
    assert list(j2) == []

    j3 = journal.Reader(journal.CURRENT_USER, path=fd)
    assert list(j3) == []

def test_reader_as_cm(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        assert not j.closed
    assert j.closed
    # make sure that operations on the Reader fail
    with pytest.raises(OSError):
        next(j)

def test_reader_messageid_match(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        j.messageid_match(id128.SD_MESSAGE_JOURNAL_START)
        j.messageid_match(id128.SD_MESSAGE_JOURNAL_STOP.hex)

def test_reader_this_boot(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        j.this_boot()
        j.this_boot(TEST_MID)
        j.this_boot(TEST_MID.hex)

def test_reader_this_machine(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        j.this_machine()
        j.this_machine(TEST_MID)
        j.this_machine(TEST_MID.hex)

def test_reader_query_unique(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        with skip_enosys():
            ans = j.query_unique('FOOBAR')
    assert isinstance(ans, set)
    assert ans == set()

def test_reader_enumerate_fields(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        with skip_enosys():
            ans = j.enumerate_fields()
    assert isinstance(ans, set)
    assert ans == set()

def test_reader_has_runtime_files(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        with skip_enosys():
            ans = j.has_runtime_files()
    assert ans == False

def test_reader_has_persistent_files(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        with skip_enosys():
            ans = j.has_runtime_files()
    assert ans == False

def test_reader_converters(tmpdir):
    converters = {'xxx' : lambda arg: 'yyy'}
    j = journal.Reader(path=tmpdir.strpath, converters=converters)

    val = j._convert_field('xxx', b'abc')
    assert val == 'yyy'

    val = j._convert_field('zzz', b'\200\200')
    assert val == b'\200\200'

def test_reader_convert_entry(tmpdir):
    converters = {'x1' : lambda arg: 'yyy',
                  'x2' : lambda arg: 'YYY'}
    j = journal.Reader(path=tmpdir.strpath, converters=converters)

    val = j._convert_entry({'x1' : b'abc',
                            'y1' : b'\200\200',
                            'x2' : [b'abc', b'def'],
                            'y2' : [b'\200\200', b'\200\201']})
    assert val == {'x1' : 'yyy',
                   'y1' : b'\200\200',
                   'x2' : ['YYY', 'YYY'],
                   'y2' : [b'\200\200', b'\200\201']}

def test_seek_realtime(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)

    now = time.time()
    j.seek_realtime(now)

    j.seek_realtime(12345)

    long_ago = datetime.datetime(1970, 5, 4)
    j.seek_realtime(long_ago)
