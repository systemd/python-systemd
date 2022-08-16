from __future__ import print_function
import contextlib
import datetime
import errno
import logging
import os
import time
import uuid
import sys
import traceback

from systemd import journal, id128
from systemd.journal import _make_line

import pytest

TEST_MID = uuid.UUID('8441372f8dca4ca98694a6091fd8519f')
TEST_MID2 = uuid.UUID('8441370000000000000000001fd85000')

class MockSender:
    def __init__(self):
        self.buf = []

    def send(self, MESSAGE, MESSAGE_ID=None,
             CODE_FILE=None, CODE_LINE=None, CODE_FUNC=None,
             **kwargs):
        args = ['MESSAGE=' + MESSAGE]

        if MESSAGE_ID is not None:
            id = getattr(MESSAGE_ID, 'hex', MESSAGE_ID)
            args.append('MESSAGE_ID=' + id)

        if CODE_LINE is CODE_FILE is CODE_FUNC is None:
            CODE_FILE, CODE_LINE, CODE_FUNC = traceback.extract_stack(limit=2)[0][:3]
        if CODE_FILE is not None:
            args.append('CODE_FILE=' + CODE_FILE)
        if CODE_LINE is not None:
            args.append('CODE_LINE={:d}'.format(CODE_LINE))
        if CODE_FUNC is not None:
            args.append('CODE_FUNC=' + CODE_FUNC)

        args.extend(_make_line(key, val) for key, val in kwargs.items())
        self.buf.append(args)

@contextlib.contextmanager
def skip_oserror(code):
    try:
        yield
    except (OSError, IOError) as e:
        if e.errno == code:
            pytest.skip()
        raise

@contextlib.contextmanager
def skip_valueerror():
    try:
        yield
    except ValueError:
        pytest.skip()

def test_priorities():
    p = journal.JournalHandler.map_priority

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
    with pytest.raises(ValueError):
        journal.JournalHandler.with_args(kw)

def test_journalhandler_init():
    kw = {'X':3, 'X3':4}
    journal.JournalHandler(logging.INFO, **kw)
    kw['level'] = logging.INFO
    journal.JournalHandler.with_args(kw)

def test_journalhandler_info():
    record = logging.LogRecord('test-logger', logging.INFO, 'testpath', 1, 'test', None, None)

    sender = MockSender()
    kw = {'X':3, 'X3':4, 'sender_function': sender.send}
    handler = journal.JournalHandler(logging.INFO, **kw)
    handler.emit(record)
    assert len(sender.buf) == 1
    assert 'X=3' in sender.buf[0]
    assert 'X3=4' in sender.buf[0]

    sender = MockSender()
    handler = journal.JournalHandler.with_args({'level':logging.INFO, 'X':3, 'X3':4, 'sender_function':sender.send})
    handler.emit(record)
    assert len(sender.buf) == 1
    assert 'X=3' in sender.buf[0]
    assert 'X3=4' in sender.buf[0]

    # just check that args==None doesn't cause an error
    journal.JournalHandler.with_args()

def test_journalhandler_no_message_id():
    record = logging.LogRecord('test-logger', logging.INFO, 'testpath', 1, 'test', None, None)
    sender = MockSender()
    handler = journal.JournalHandler(logging.INFO, sender_function=sender.send)
    handler.emit(record)
    assert len(sender.buf) == 1
    assert all(not m.startswith('MESSAGE_ID=') for m in sender.buf[0])

def test_journalhandler_message_id_on_handler():
    record = logging.LogRecord('test-logger', logging.INFO, 'testpath', 1, 'test', None, None)
    sender = MockSender()
    handler = journal.JournalHandler(logging.INFO, sender_function=sender.send,
                                     MESSAGE_ID=TEST_MID)
    handler.emit(record)
    assert len(sender.buf) == 1
    assert 'MESSAGE_ID=' + TEST_MID.hex in sender.buf[0]

def test_journalhandler_message_id_on_handler_hex():
    record = logging.LogRecord('test-logger', logging.INFO, 'testpath', 1, 'test', None, None)
    sender = MockSender()
    handler = journal.JournalHandler(logging.INFO, sender_function=sender.send,
                                     MESSAGE_ID=TEST_MID.hex)
    handler.emit(record)
    assert len(sender.buf) == 1
    assert 'MESSAGE_ID=' + TEST_MID.hex in sender.buf[0]

def test_journalhandler_message_id_on_message():
    record = logging.LogRecord('test-logger', logging.INFO, 'testpath', 1, 'test', None, None)
    record.__dict__['MESSAGE_ID'] = TEST_MID2
    sender = MockSender()
    handler = journal.JournalHandler(logging.INFO, sender_function=sender.send,
                                     MESSAGE_ID=TEST_MID)
    handler.emit(record)
    assert len(sender.buf) == 1
    assert 'MESSAGE_ID=' + TEST_MID2.hex in sender.buf[0]

def test_journalhandler_message_id_on_message_hex():
    record = logging.LogRecord('test-logger', logging.INFO, 'testpath', 1, 'test', None, None)
    record.__dict__['MESSAGE_ID'] = TEST_MID2.hex
    sender = MockSender()
    handler = journal.JournalHandler(logging.INFO, sender_function=sender.send,
                                     MESSAGE_ID=TEST_MID)
    handler.emit(record)
    assert len(sender.buf) == 1
    assert 'MESSAGE_ID=' + TEST_MID2.hex in sender.buf[0]

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

    with skip_oserror(errno.ENOSYS):
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
        with skip_oserror(errno.ENOSYS):
            ans = j.query_unique('FOOBAR')
    assert isinstance(ans, set)
    assert ans == set()

def test_reader_enumerate_fields(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        with skip_oserror(errno.ENOSYS):
            ans = j.enumerate_fields()
    assert isinstance(ans, set)
    assert ans == set()

def test_reader_has_runtime_files(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        with skip_oserror(errno.ENOSYS):
            ans = j.has_runtime_files()
    assert ans is False

def test_reader_has_persistent_files(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with j:
        with skip_oserror(errno.ENOSYS):
            ans = j.has_runtime_files()
    assert ans is False

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

def test_reader_convert_timestamps(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)

    val = j._convert_field('_SOURCE_REALTIME_TIMESTAMP', 1641651559324187)
    if sys.version_info >= (3,):
        assert val.tzinfo is not None

    val = j._convert_field('__REALTIME_TIMESTAMP', 1641651559324187)
    if sys.version_info >= (3,):
        assert val.tzinfo is not None

    val = j._convert_field('COREDUMP_TIMESTAMP', 1641651559324187)
    if sys.version_info >= (3,):
        assert val.tzinfo is not None

def test_seek_realtime(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)

    now = time.time()
    j.seek_realtime(now)

    j.seek_realtime(12345)

    long_ago = datetime.datetime(1970, 5, 4)
    j.seek_realtime(long_ago)

def test_journal_stream():
    # This will fail when running in a bare chroot without /run/systemd/journal/stdout
    with skip_oserror(errno.ENOENT):
        stream = journal.stream('test_journal.py')

    res = stream.write('message...\n')
    assert res in (11, None) # Python2 returns None

    print('printed message...', file=stream)
