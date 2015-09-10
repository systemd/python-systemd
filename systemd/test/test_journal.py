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
