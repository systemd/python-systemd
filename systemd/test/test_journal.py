import logging
from systemd import journal

import pytest

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
    j5 = journal.Reader(journal.LOCAL_ONLY|
                        journal.RUNTIME_ONLY|
                        journal.SYSTEM_ONLY)
    j6 = journal.Reader(0)

def test_reader_init_path(tmpdir):
    j = journal.Reader(path=tmpdir.strpath)
    with pytest.raises(ValueError):
        journal.Reader(journal.LOCAL_ONLY, path=tmpdir.strpath)

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
