# SPDX-License-Identifier: LGPL-2.1-or-later

from systemd._reader import _Reader

import pytest

class SequenceWithoutLength:
    def __getitem__(self, index: int) -> int:
        return 5

    # no __length__ implementation

def test_reader_init_with_empty_files_sequence():
    _Reader(files=[], flags=0)

def test_reader_init_with_sequence_without_length():
    with pytest.raises(TypeError):
        _Reader(files=SequenceWithoutLength(), flags=0)
