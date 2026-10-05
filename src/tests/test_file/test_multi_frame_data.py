import numpy as np
import pytest

from dliswriter.file.file import DLISFile
from dliswriter.file.multi_frame_data import MultiFrameData
from dliswriter.file.writer import DLISWriter
from dliswriter.utils.source_data_wrappers import DictDataWrapper
from ._incremental_test_helpers import definition, synthetic_data, readback


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


def test_same_writer_composes_metadata_and_offset_batches(tmp_path, caplog):
    data = synthetic_data()
    df, frame = definition(data)
    path = tmp_path / 'composed.dlis'
    writer = DLISWriter(path, visible_record_length=df.storage_unit_label.max_record_length)
    writer.write_storage_unit_label(df.storage_unit_label)
    # Exactly one LF, no NoFormat: [[]] emits only the existing EFLRs.
    writer.write_logical_records(list(df.generator([[]])), output_chunk_size=2**20)
    for start in (0, 100):
        batch = {name: values[start:start + 100] for name, values in data.items()}
        wrapper = DictDataWrapper(batch, mapping=frame.channel_name_mapping,
                                  known_dtypes=frame.known_channel_dtypes_mapping)
        # Materialize this bounded batch: progressbar may restart a self-iterator.
        records = list(MultiFrameData(frame, wrapper, first_frame_number=start + 1))
        assert len(records) == 100
        writer.write_logical_records(records, output_chunk_size=2**20)
    readback(path, data, 200, caplog)
