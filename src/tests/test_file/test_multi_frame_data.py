import numpy as np
import pytest

from dliswriter.file.file import DLISFile
from dliswriter.file.multi_frame_data import MultiFrameData
from dliswriter.utils.source_data_wrappers import DictDataWrapper


@pytest.fixture
def frame_and_data():
    lf = DLISFile().add_logical_file()
    channel = lf.add_channel('VALUE', cast_dtype=np.float32, dimension=[1], element_limit=[1])
    frame = lf.add_frame('FRAME', channels=[channel])
    data = DictDataWrapper({'VALUE': np.arange(3, dtype=np.float32)}, mapping={'VALUE': 'VALUE'})
    return frame, data


def assert_rows(records, first):
    assert len(records) == 3
    assert [row._frame_number for row in records] == list(range(first, first + 3))
    np.testing.assert_array_equal([row._slots['VALUE'] for row in records], [0, 1, 2])


def test_default_numbering(frame_and_data):
    records = MultiFrameData(*frame_and_data)
    assert len(records) == 3
    assert_rows(list(records), 1)
    assert_rows(list(records), 1)


@pytest.mark.parametrize('first', [1, 101, 201])
@pytest.mark.parametrize('chunk_size', [None, 1, 2])
def test_offset_length_exhaustion_and_reiteration(frame_and_data, first, chunk_size):
    records = MultiFrameData(*frame_and_data, chunk_size=chunk_size, first_frame_number=first)
    assert len(records) == 3
    assert_rows(list(records), first)
    with pytest.raises(StopIteration):
        next(records)
    assert len(records) == 3
    assert_rows(list(records), first)


@pytest.mark.parametrize('first', [0, -1, -100])
def test_nonpositive_offset(frame_and_data, first):
    with pytest.raises(ValueError, match='first_frame_number'):
        MultiFrameData(*frame_and_data, first_frame_number=first)


@pytest.mark.parametrize('first', [True, False, 1.0, 1.5, '1', None])
def test_noninteger_offset(frame_and_data, first):
    with pytest.raises(TypeError, match='first_frame_number must be'):
        MultiFrameData(*frame_and_data, first_frame_number=first)
