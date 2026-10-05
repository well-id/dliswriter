"""Public same-session writing: strict readback and pre-emission safety."""

import h5py
import numpy as np
import pytest
import struct

from dliswriter import DLISFile, RepresentationCode
from dliswriter.file.writer import ByteWriter
from ._incremental_test_helpers import definition, synthetic_data, readback


def batch(data, start=0, stop=100):
    return {name: values[start:stop] for name, values in data.items()}


@pytest.mark.parametrize('kind', ['parameter', 'computation'])
@pytest.mark.parametrize('with_axis', [False, True])
def test_scalar_metadata_serialized_once(tmp_path, caplog, kind, with_axis):
    from dlisio import dlis
    from dlisio.common import Actions, ErrorHandler

    def make_definition():
        df, _ = definition(synthetic_data())
        lf = df.logical_files[0]
        kwargs = {'values': [12.5]}
        if with_axis:
            kwargs['axis'] = [lf.add_axis('AXIS', coordinates=[0.0, 1.0])]
            kwargs['zones'] = [lf.add_zone('ZONE')]
        getattr(lf, 'add_' + kind)('VALUE', **kwargs)
        return df

    data = batch(synthetic_data())
    conventional = tmp_path / 'conventional.dlis'
    make_definition().write(conventional, data=data, output_chunk_size=8192)
    path = tmp_path / 'incremental.dlis'
    make_definition().start_incremental(path, data).close()
    assert path.stat().st_size > 80
    handler = ErrorHandler(info=Actions.RAISE, minor=Actions.RAISE,
                           major=Actions.RAISE, critical=Actions.RAISE)
    caplog.clear()
    for target in (conventional, path):
        with dlis.load(str(target), error_handler=handler) as physical:
            lf = physical[0]
            item = getattr(lf, kind + 's')[0]
            assert item.name == 'VALUE' and item.dimension == [1]
            np.testing.assert_array_equal(item.values, [12.5])
            if with_axis:
                assert item.axis[0].name == 'AXIS'
                assert item.axis[0].coordinates == [0.0, 1.0]
                assert item.zones[0].name == 'ZONE'
            assert len(lf.frames[0].curves()) == 100
    assert not caplog.records


def test_startup_and_append_commit_prepared_bytes_not_mutated_records(tmp_path, monkeypatch, caplog):
    from dliswriter.file.writer import DLISWriter
    from dliswriter.logical_record.core.eflr import EFLRSet
    from dliswriter.logical_record.iflr_types import FrameData
    from dliswriter.logical_record.misc import StorageUnitLabel

    calls, records, expected = {}, [], []
    for cls in (EFLRSet, FrameData, StorageUnitLabel):
        original = cls.represent_as_bytes

        def once(self, original=original):
            key = id(self)
            calls[key] = calls.get(key, 0) + 1
            assert calls[key] == 1, 'record serialized twice'
            records.append(self)  # retain identity across both batches
            return original(self)

        monkeypatch.setattr(cls, 'represent_as_bytes', once)

    original_commit = getattr(DLISWriter, '_commit_prepared', None)

    def commit(self, prepared, read_size, *, includes_sul=False):
        assert prepared.tell() == 0
        expected.append(prepared.read())  # small fixture only; production reads are bounded
        prepared.seek(0)
        for record in records:
            if isinstance(record, FrameData):
                record._slots['SIGNAL'] = -999
                record._frame_number = 999
        count = dict(calls)
        result = original_commit(self, prepared, read_size, includes_sul=includes_sul)
        assert calls == count
        return result

    monkeypatch.setattr(DLISWriter, '_commit_prepared', commit, raising=False)
    data = synthetic_data()
    df, _ = definition(data)
    path = tmp_path / 'prepared.dlis'
    with df.start_incremental(path, batch(data)) as stream:
        stream.append(batch(data, 100, 200))
    assert len(expected) == 2 and path.read_bytes() == b''.join(expected)
    assert set(calls.values()) == {1}
    assert sum(isinstance(record, FrameData) for record in records) == 200
    assert sum(isinstance(record, StorageUnitLabel) for record in records) == 1
    readback(path, data, 200, caplog)


@pytest.mark.parametrize('rows, rolled', [(100, False), (24000, True)])
def test_prepared_spool_spills_and_commit_reads_are_bounded(tmp_path, monkeypatch, rows, rolled):
    import tempfile
    from dliswriter.file import incremental_writer
    from dliswriter.file.writer import DLISWriter

    spools, reads, writes = [], [], []

    class ObservedSpool(tempfile.SpooledTemporaryFile):
        def read(self, size=-1):
            assert 0 < size <= incremental_writer._PREPARED_MAX_SIZE
            reads.append(size)
            return super().read(size)

    def create(*args, **kwargs):
        assert kwargs == {'max_size': 2**20, 'mode': 'w+b'}
        spool = ObservedSpool(*args, **kwargs)
        spools.append(spool)
        return spool

    original_commit = DLISWriter._commit_prepared

    def commit(self, prepared, read_size, *, includes_sul=False):
        assert prepared._rolled is rolled
        return original_commit(self, prepared, read_size, includes_sul=includes_sul)

    original_write = ByteWriter.write_bytes

    def write(self, bts, size=None):
        assert 0 < len(bts) <= 2**20
        writes.append(len(bts))
        return original_write(self, bts, size)

    monkeypatch.setattr(incremental_writer, 'SpooledTemporaryFile', create)
    monkeypatch.setattr(DLISWriter, '_commit_prepared', commit)
    monkeypatch.setattr(ByteWriter, 'write_bytes', write)
    data = synthetic_data()
    df, _ = definition(data)
    source = {name: np.tile(values, (rows // 100, 1) if values.ndim == 2 else rows // 100)
              for name, values in batch(data).items()}
    path = tmp_path / 'spooled.dlis'
    # A huge output setting must not make the spool or copy read unbounded.
    with df.start_incremental(path, source, output_chunk_size=2**30) as stream:
        stream.append(source)
        assert stream._next_frame_number == 2 * rows + 1
    assert len(spools) == 2 and all(spool.closed for spool in spools)
    assert reads and set(reads) == {2**20}
    assert sum(writes) == path.stat().st_size
    if rolled:
        assert path.stat().st_size > 2 * 2**20


def failing_spool_factory(failure, spools):
    import tempfile

    class FailingSpool(tempfile.SpooledTemporaryFile):
        def __exit__(self, exc_type, exc_value, traceback):
            self.close()

        def write(self, bts):
            result = super().write(bts)
            if failure == 'spool_write':
                raise OSError('simulated spool_write')
            return result

        def read(self, size=-1):
            if failure == 'commit_read' and self.tell() > 0:
                raise OSError('simulated commit_read')
            return super().read(size)

        def close(self):
            was_closed = self.closed
            super().close()
            if failure == 'close' and not was_closed:
                raise OSError('simulated close')

    def create(*args, **kwargs):
        spool = FailingSpool(*args, **kwargs)
        spools.append(spool)
        return spool

    return create


def assert_failure_boundary(path, before, stream, data, preparation_failure):
    if preparation_failure:
        assert path.read_bytes() == before if before else not path.exists()
    else:
        assert path.stat().st_size > len(before)
        assert path.read_bytes().startswith(before)
    if stream is None:
        return
    assert stream._next_frame_number == 101
    assert stream._failed is not preparation_failure
    if preparation_failure:
        stream.append(batch(data, 100, 200))
        assert stream._next_frame_number == 201
    else:
        with pytest.raises(RuntimeError, match='failed'):
            stream.append(batch(data, 100, 200))
    completed = path.read_bytes()
    stream.close()
    stream.close()
    assert path.read_bytes() == completed


@pytest.mark.parametrize('startup', [False, True])
@pytest.mark.parametrize('failure', ['serialization', 'spool_write', 'commit_read', 'commit_write', 'close'])
def test_prepared_cleanup_and_failure_boundary(tmp_path, monkeypatch, startup, failure):
    from dliswriter.file import incremental_writer
    from dliswriter.logical_record.iflr_types import FrameData

    data = synthetic_data()
    df, _ = definition(data)
    path = tmp_path / 'cleanup.dlis'
    df.storage_unit_label.max_record_length = 128
    stream = None if startup else df.start_incremental(path, batch(data), output_chunk_size=128)
    before = b'' if startup else path.read_bytes()
    spools = []
    original_serialize = FrameData.represent_as_bytes
    original_write = ByteWriter.write_bytes

    def serialize(self):
        result = original_serialize(self)
        if failure == 'serialization' and self._frame_number % 100 == 0:
            raise OSError('simulated serialization')
        return result

    def write(self, bts, size=None):
        if failure == 'commit_write':
            original_write(self, bts[:10])
            raise OSError('simulated commit_write')
        return original_write(self, bts, size)

    with monkeypatch.context() as patch:
        patch.setattr(incremental_writer, 'SpooledTemporaryFile', failing_spool_factory(failure, spools))
        patch.setattr(FrameData, 'represent_as_bytes', serialize)
        patch.setattr(ByteWriter, 'write_bytes', write)
        with pytest.raises(OSError, match=f'simulated {failure}'):
            if startup:
                df.start_incremental(path, batch(data), output_chunk_size=128)
            else:
                stream.append(batch(data, 100, 200))
    assert len(spools) == 1 and spools[0].closed
    preparation_failure = failure in ('serialization', 'spool_write')
    assert_failure_boundary(path, before, stream, data, preparation_failure)
    if startup and preparation_failure:
        df.start_incremental(path, batch(data)).close()


def test_public_checkpoints_and_equivalence(tmp_path, caplog, monkeypatch):
    from dliswriter import IncrementalDLISWriter
    from dliswriter.file import IncrementalDLISWriter as FileExport
    from dliswriter.logical_record.eflr_types.channel import ChannelItem
    from dliswriter.logical_record.eflr_types.frame import FrameItem

    assert FileExport is IncrementalDLISWriter
    data = synthetic_data()
    df, frame = definition(data)
    normal, _ = definition(data)
    # Small visible records force segmentation as well as buffer flushes.
    df.storage_unit_label.max_record_length = 128
    normal.storage_unit_label.max_record_length = 128
    path, baseline = tmp_path / 'stream.dlis', tmp_path / 'normal.dlis'
    normal.write(baseline, data=data, output_chunk_size=128)
    expected_curves, expected_metadata = readback(baseline, data, 300, caplog)

    def no_batch_inference(*args, **kwargs):
        raise AssertionError('Incremental writing must not infer or reset acquisition metadata')

    # Class-level guards also cover the session's detached metadata objects.
    monkeypatch.setattr(FrameItem, 'setup_from_data', no_batch_inference)
    monkeypatch.setattr(ChannelItem, 'set_dimension_and_repr_code_from_data', no_batch_inference)
    writes = []
    original = ByteWriter.write_bytes

    def observe(self, bts, size=None):
        writes.append(len(bts))
        return original(self, bts, size)

    monkeypatch.setattr(ByteWriter, 'write_bytes', observe)
    stream = df.start_incremental(path, batch(data), output_chunk_size=128)
    assert isinstance(stream, IncrementalDLISWriter)
    prefix = b''
    for count in (100, 200, 300):
        if count > 100:
            stream.append(batch(data, count - 100, count))
        current = path.read_bytes()
        assert len(current) > len(prefix) and current.startswith(prefix)
        prefix = current
        curves, metadata = readback(path, data, count, caplog)
        assert metadata == expected_metadata
    assert len(writes) > 100  # not merely a final-buffer flush
    np.testing.assert_array_equal(curves, expected_curves)
    stream.close()
    stream.close()
    assert path.read_bytes() == prefix
    with pytest.raises(RuntimeError, match='closed'):
        stream.append(batch(data))


@pytest.mark.parametrize('kind', ['missing', 'unequal', 'empty', 'shape', 'ndim',
                                  'object', 'string', 'complex', 'unsafe', 'scalar'])
def test_invalid_batch_is_unchanged_and_retryable(tmp_path, kind):
    data = synthetic_data()
    df, _ = definition(data)
    # Stored channel data must not fill missing batch channels.
    df.logical_files[0]._data_dict.update(data)
    path = tmp_path / 'stream.dlis'
    with df.start_incremental(path, batch(data), output_chunk_size=8192) as stream:
        bad = batch(data)
        if kind == 'missing':
            del bad['VECTOR']
        elif kind == 'unequal':
            bad['VECTOR'] = bad['VECTOR'][:-1]
        elif kind == 'empty':
            bad = batch(data, 0, 0)
        elif kind == 'shape':
            bad['VECTOR'] = np.zeros((100, 2), dtype=np.float32)
        elif kind == 'ndim':
            bad['VECTOR'] = np.zeros((100, 1, 3), dtype=np.float32)
        elif kind == 'scalar':
            bad['SIGNAL'] = np.array(1, dtype=np.float32)
        else:
            dtype = {'object': object, 'string': 'U4', 'complex': np.complex64,
                     'unsafe': np.float64}[kind]
            bad['SIGNAL'] = bad['SIGNAL'].astype(dtype)
        before = path.read_bytes()
        counter = stream._next_frame_number
        with pytest.raises((ValueError, TypeError, RuntimeError)):
            stream.append(bad)
        assert path.read_bytes() == before
        assert stream._next_frame_number == counter
        stream.append(batch(data, 100, 200))
        assert stream._next_frame_number == 201
        invalid_path = tmp_path / 'invalid-initial.dlis'
        with pytest.raises((ValueError, TypeError, RuntimeError)):
            df.start_incremental(invalid_path, bad)
        assert not invalid_path.exists()


def invalidate_frame_schema(frame, kind):
    """Introduce one of the tested channel/schema inconsistencies."""
    if kind == 'dimension':
        frame.channels.value[-1].dimension.value = [2]
    elif kind == 'repr':
        frame.channels.value[-1].representation_code._value = RepresentationCode.FDOUBL
    elif kind == 'limit':
        frame.channels.value[-1].element_limit.value = [2]
    elif kind == 'duplicate':
        frame.channels.value.append(frame.channels.value[0])
    elif kind == 'mapping':
        frame.channels.value[-1].dataset_name = frame.channels.value[0].dataset_name
    else:
        frame.channels.value = frame.channels.value[:-1]


@pytest.mark.parametrize('kind', ['lf', 'no_lf', 'frame', 'no_frame', 'noformat',
                                  'dimension', 'repr', 'limit', 'origin', 'metadata',
                                  'channels', 'duplicate', 'mapping'])
def test_invalid_definition_preflight(tmp_path, kind):
    data = synthetic_data()
    df, frame = definition(data)
    lf = df.logical_files[0]
    if kind == 'lf':
        df.add_logical_file()
    elif kind == 'no_lf':
        df.logical_files.clear()
    elif kind == 'frame':
        lf.add_frame('SECOND', channels=frame.channels.value)
    elif kind == 'no_frame':
        lf._eflr_sets.pop(type(frame.parent))
    elif kind == 'noformat':
        lf._no_format_frame_data.append(object())
    elif kind == 'origin':
        lf.defining_origin.file_id.value = 'WRONG'
    elif kind == 'metadata':
        frame.description.value = 'Non-ASCII \u2603'
    else:
        invalidate_frame_schema(frame, kind)
    path = tmp_path / 'invalid.dlis'
    with pytest.raises((ValueError, TypeError, RuntimeError, UnicodeError)):
        df.start_incremental(path, batch(data), output_chunk_size=8192)
    assert not path.exists()


@pytest.mark.parametrize('size', [0, -1, 1, 8192.5, None, True, '8192', float('inf')])
def test_invalid_buffer_preflight(tmp_path, size):
    df, _ = definition(synthetic_data())
    path = tmp_path / 'invalid.dlis'
    with pytest.raises((ValueError, TypeError)):
        df.start_incremental(path, batch(synthetic_data()), output_chunk_size=size)
    assert not path.exists()


def test_existing_target_never_truncated(tmp_path):
    df, _ = definition(synthetic_data())
    path = tmp_path / 'existing.dlis'
    path.write_bytes(b'preserve me')
    with pytest.raises(FileExistsError):
        df.start_incremental(path, batch(synthetic_data()))
    assert path.read_bytes() == b'preserve me'
    dangling = tmp_path / 'dangling.dlis'
    dangling.symlink_to(tmp_path / 'absent.dlis')
    with pytest.raises(FileExistsError):
        df.start_incremental(dangling, batch(synthetic_data()))
    assert not (tmp_path / 'absent.dlis').exists()


@pytest.mark.parametrize('form', ['dict', 'numpy', 'hdf5'])
def test_aliases_order_endian_and_detached_metadata(tmp_path, caplog, form):
    data = synthetic_data()
    df, frame = definition(data)
    for channel in frame.channels.value:
        channel.dataset_name = 'alias_' + channel.name

    def source(start, stop):
        aliased = {'alias_' + name: values[start:stop].astype(values.dtype.newbyteorder('>'))
                   for name, values in reversed(list(data.items()))}
        if form == 'dict':
            return aliased
        if form == 'numpy':
            arr = np.empty(stop - start, dtype=[
                (name, values.dtype, values.shape[1:]) for name, values in aliased.items()])
            for name, values in aliased.items():
                arr[name] = values
            return arr
        path = tmp_path / f'batch{start}.h5'
        with h5py.File(path, 'w') as handle:
            for name, values in aliased.items():
                handle[name] = values
        return path

    path = tmp_path / 'stream.dlis'
    with df.start_incremental(path, source(0, 100)) as stream:
        # All these changes must be isolated from the live session.
        frame.name = 'MUTATED'
        frame.index_max.value = 0
        frame.channels.value[0].dataset_name = 'missing'
        frame.channels.value[-1].dimension.value = [99]
        df.logical_files.clear()
        stream.append(source(100, 200))
        readback(path, data, 200, caplog)


def test_inference_does_not_infer_acquisition_bounds(tmp_path):
    from dlisio import dlis

    df = DLISFile()
    lf = df.add_logical_file()
    lf.add_origin('ORIGIN', origin_reference=1)
    scalar = lf.add_channel('X')
    vector = lf.add_channel('V', element_limit=[5])
    frame = lf.add_frame('FRAME', channels=[scalar, vector])
    data = {'X': np.arange(3, dtype=np.float64), 'V': np.ones((3, 2), np.float32)}
    path = tmp_path / 'inferred.dlis'
    with df.start_incremental(path, data) as stream:
        stream.append(data)
    assert scalar.cast_dtype is None and scalar.dimension.value is None
    assert frame.index_max.value is None
    with dlis.load(str(path)) as physical:
        parsed = physical[0].frames[0]
        assert parsed.index_min is None and parsed.index_max is None
        assert parsed.spacing is None and parsed.direction is None
        assert parsed.channels[1].dimension == [2]
        assert parsed.channels[1].element_limit == [5]
        np.testing.assert_array_equal(parsed.curves()['FRAMENO'], np.arange(1, 7))


def test_emission_failure_poisoned_and_counter_unchanged(tmp_path, monkeypatch):
    data = synthetic_data()
    df, frame = definition(data)
    data['VECTOR'] = np.tile(data['VECTOR'], (1, 40))
    frame.channels.value[-1].dimension.value = [120]
    frame.channels.value[-1].element_limit.value = [120]
    df.storage_unit_label.max_record_length = 128
    path = tmp_path / 'failed.dlis'
    stream = df.start_incremental(path, batch(data), output_chunk_size=128)
    writer = stream._writer._byte_writer
    original = writer.write_bytes
    before = path.read_bytes()
    calls = []

    def partial(bts, size=None):
        calls.append(len(bts))
        original(bts[:10])
        raise OSError('simulated partial write')

    monkeypatch.setattr(writer, 'write_bytes', partial)
    with pytest.raises(OSError, match='partial'):
        stream.append(batch(data, 100, 200))
    assert calls == [128] and path.read_bytes().startswith(before)
    assert len(path.read_bytes()) > len(before)
    assert stream._next_frame_number == 101
    with pytest.raises(RuntimeError, match='failed'):
        stream.append(batch(data))
    stream.close()
    stream.close()


def test_counter_overflow_preflight(tmp_path):
    data = synthetic_data()
    df, _ = definition(data)
    path = tmp_path / 'counter.dlis'
    with df.start_incremental(path, batch(data)) as stream:
        stream._next_frame_number = 2**30 - 1
        before = path.read_bytes()
        with pytest.raises(struct.error):
            stream.append(batch(data, 0, 2))
        assert path.read_bytes() == before
        assert stream._next_frame_number == 2**30 - 1


@pytest.mark.parametrize('invalid', [False, True])
def test_hdf5_handle_closed_on_success_and_failure(tmp_path, monkeypatch, invalid):
    data = synthetic_data()
    source = tmp_path / 'batch.h5'
    with h5py.File(source, 'w') as handle:
        for name, values in batch(data).items():
            if invalid and name == 'VECTOR':
                continue
            handle[name] = values
    opened = []
    original = h5py.File

    def track(*args, **kwargs):
        handle = original(*args, **kwargs)
        opened.append(handle)
        return handle

    monkeypatch.setattr(h5py, 'File', track)
    df, _ = definition(data)
    path = tmp_path / 'stream.dlis'
    if invalid:
        with pytest.raises(KeyError):
            df.start_incremental(path, source)
        assert not path.exists()
    else:
        df.start_incremental(path, source).close()
    assert opened and all(not handle.id.valid for handle in opened)


def test_safe_widening_segmented_fdata_and_context_exception(tmp_path, monkeypatch):
    from dlisio import dlis
    from dlisio.common import Actions, ErrorHandler
    from dliswriter.logical_record.iflr_types import FrameData

    df = DLISFile(max_record_length=128)
    lf = df.add_logical_file()
    lf.add_origin('ORIGIN', origin_reference=1)
    channel = lf.add_channel('X', cast_dtype=np.float64)
    lf.add_frame('FRAME', channels=[channel])
    data = {'X': np.arange(300, dtype=np.float32).reshape(3, 100)}
    path = tmp_path / 'wide.dlis'
    with pytest.raises(LookupError):
        with df.start_incremental(path, data, output_chunk_size=128) as stream:
            original = stream._writer._iter_visible_records

            def only_fdata(records):
                assert all(isinstance(record, FrameData) for record in records)
                segments = list(original(records))
                assert len(segments) > len(records)
                yield from segments

            monkeypatch.setattr(stream._writer, '_iter_visible_records', only_fdata)
            stream.append(data)
            raise LookupError('application error closes context')
    with pytest.raises(RuntimeError, match='closed'):
        stream.append(data)
    handler = ErrorHandler(info=Actions.RAISE, minor=Actions.RAISE,
                           major=Actions.RAISE, critical=Actions.RAISE)
    with dlis.load(str(path), error_handler=handler) as physical:
        curves = physical[0].frames[0].curves()
        assert curves['X'].dtype == np.float64
        np.testing.assert_array_equal(curves['X'], np.concatenate([data['X'], data['X']]))


def test_short_fdata_preflight_leaves_no_target(tmp_path):
    df = DLISFile()
    lf = df.add_logical_file()
    lf.add_origin('ORIGIN', origin_reference=1)
    channel = lf.add_channel('X')
    lf.add_frame('F', channels=[channel], origin_reference=1)
    path = tmp_path / 'short.dlis'
    with pytest.raises(ValueError, match='shorter than 12'):
        df.start_incremental(path, {'X': np.array([1], dtype=np.float32)})
    assert not path.exists()


@pytest.mark.parametrize('length', [20, 22, 24, 26, 28, 30])
def test_segment_invalid_record_length_leaves_no_target(tmp_path, length):
    data = synthetic_data()
    df, _ = definition(data)
    df.storage_unit_label.max_record_length = length
    path = tmp_path / 'invalid-segments.dlis'
    with pytest.raises(ValueError, match='cannot be less than 24'):
        df.start_incremental(path, batch(data))
    assert not path.exists()


def test_metadata_segmentation_preflight_leaves_no_target(tmp_path, monkeypatch):
    from dliswriter.logical_record.core.logical_record.logical_record_bytes import LogicalRecordBytes

    original = LogicalRecordBytes.make_segments

    def fail_after_segment(self, size):
        yield from original(self, size)
        if self._is_eflr:
            raise ValueError('simulated metadata segmentation failure')

    monkeypatch.setattr(LogicalRecordBytes, 'make_segments', fail_after_segment)
    data = synthetic_data()
    df, _ = definition(data)
    path = tmp_path / 'metadata.dlis'
    with pytest.raises(ValueError, match='metadata segmentation'):
        df.start_incremental(path, batch(data))
    assert not path.exists()


@pytest.mark.parametrize('failure', ['serialization', 'segmentation'])
def test_late_record_preflight_preserves_append_and_retry(tmp_path, monkeypatch, caplog, failure):
    from dliswriter.logical_record.iflr_types import FrameData

    data = synthetic_data()
    df, _ = definition(data)
    path = tmp_path / 'retry.dlis'
    with df.start_incremental(path, batch(data), output_chunk_size=8192) as stream:
        before = path.read_bytes()
        counter = stream._next_frame_number
        original = FrameData.represent_as_bytes

        def fail_last(self):
            result = original(self)
            if self._frame_number == 200:
                if failure == 'serialization':
                    raise ValueError('simulated serialization failure')
                segments = result.make_segments

                def fail_after_segment(size):
                    yield from segments(size)
                    raise ValueError('simulated segmentation failure')

                result.make_segments = fail_after_segment
            return result

        with monkeypatch.context() as patch:
            patch.setattr(FrameData, 'represent_as_bytes', fail_last)
            with pytest.raises(ValueError, match=f'simulated {failure}'):
                stream.append(batch(data, 100, 200))
        assert path.read_bytes() == before
        assert stream._next_frame_number == counter
        stream.append(batch(data, 100, 200))
        assert stream._next_frame_number == 201
        readback(path, data, 200, caplog)


@pytest.mark.parametrize('index_type', ['BOREHOLE-DEPTH', 'CUSTOM-INDEX'])
def test_explicit_vector_index_rejected_before_output(tmp_path, index_type):
    data = synthetic_data()
    df, frame = definition(data)
    frame.channels.value = list(reversed(frame.channels.value))
    frame.index_type.value = index_type
    path = tmp_path / 'vector-index.dlis'
    with pytest.raises(RuntimeError, match='1-dimensional'):
        df.start_incremental(path, batch(data))
    assert not path.exists()


def test_implicit_vector_first_channel_strict_readback(tmp_path, caplog):
    from dlisio import dlis
    from dlisio.common import Actions, ErrorHandler

    df = DLISFile()
    lf = df.add_logical_file()
    lf.add_origin('ORIGIN', origin_reference=1)
    vector = lf.add_channel('VECTOR', element_limit=[5])
    lf.add_frame('FRAME', channels=[vector])
    data = {'VECTOR': np.arange(12, dtype=np.float32).reshape(4, 3)}
    path = tmp_path / 'implicit.dlis'
    with df.start_incremental(path, data) as stream:
        stream.append(data)
    handler = ErrorHandler(info=Actions.RAISE, minor=Actions.RAISE,
                           major=Actions.RAISE, critical=Actions.RAISE)
    caplog.clear()
    with dlis.load(str(path), error_handler=handler) as physical:
        parsed = physical[0].frames[0]
        assert parsed.index_type is None and parsed.index == 'FRAMENO'
        assert parsed.index_min is None and parsed.index_max is None
        assert parsed.spacing is None and parsed.direction is None
        curves = parsed.curves()
        np.testing.assert_array_equal(curves['FRAMENO'], np.arange(1, 9))
        np.testing.assert_array_equal(curves['VECTOR'], np.concatenate([data['VECTOR']] * 2))
        assert parsed.channels[0].element_limit == [5]
    assert not caplog.records


def test_relative_output_stays_anchored_after_chdir(tmp_path, monkeypatch, caplog):
    first, second = tmp_path / 'first', tmp_path / 'second'
    first.mkdir()
    second.mkdir()
    data = synthetic_data()
    df, _ = definition(data)
    monkeypatch.chdir(first)
    with df.start_incremental('output.dlis', batch(data)) as stream:
        monkeypatch.chdir(second)
        stream.append(batch(data, 100, 200))
        stream.append(batch(data, 200, 300))
    assert not (second / 'output.dlis').exists()
    readback(first / 'output.dlis', data, 300, caplog)


def test_snapshot_preserves_reference_graph_without_copying_stored_arrays(tmp_path, caplog):
    class NoCopyArray(np.ndarray):
        def __deepcopy__(self, memo):
            raise AssertionError('Stored acquisition arrays must not be copied')

    data = synthetic_data()
    df, frame = definition(data)
    lf = df.logical_files[0]
    stored = data['SIGNAL'].view(NoCopyArray)
    lf._data_dict['SIGNAL'] = stored
    frozen = df._snapshot_metadata()
    frozen_lf = frozen.logical_files[0]
    frozen_frame = frozen_lf.frames[0]
    assert frozen_lf is not lf and frozen_lf.physical_file is frozen
    assert frozen_lf._data_dict == {}
    assert frozen_frame.channels.value == frozen_lf.channels
    assert frozen_frame.parent is not frame.parent
    assert frozen_frame.parent is next(iter(frozen_lf._eflr_sets[type(frame.parent)].values()))
    assert frozen_frame.parent is next(iter(frozen._eflr_sets[type(frame.parent)].values()))
    for detached, original in zip(frozen_frame.channels.value, frame.channels.value):
        assert detached is not original
        assert detached.parent is not original.parent
    path = tmp_path / 'snapshot.dlis'
    with df.start_incremental(path, batch(data)) as stream:
        frame.channels.value[0].units.value = 'ft'
        stream.append(batch(data, 100, 200))
        readback(path, data, 200, caplog)
    assert lf._data_dict['SIGNAL'] is stored


@pytest.mark.parametrize('index_type', ['BOREHOLE-DEPTH', 'CUSTOM-INDEX'])
@pytest.mark.parametrize('known', [False, True])
def test_scalar_index_keeps_unknown_or_explicit_acquisition_metadata(tmp_path, caplog, index_type, known):
    from dlisio import dlis
    from dlisio.common import Actions, ErrorHandler

    data = synthetic_data()
    if known:
        df, frame = definition(data)
        frame.index_type.value = index_type
    else:
        df = DLISFile()
        lf = df.add_logical_file()
        lf.add_origin('ORIGIN', origin_reference=1)
        channels = [lf.add_channel(name) for name in data]
        lf.add_frame('FRAME', channels=channels, index_type=index_type)
    path = tmp_path / 'scalar-index.dlis'
    with df.start_incremental(path, batch(data)) as stream:
        stream.append(batch(data, 100, 200))
    handler = ErrorHandler(info=Actions.RAISE, minor=Actions.RAISE,
                           major=Actions.RAISE, critical=Actions.RAISE)
    caplog.clear()
    with dlis.load(str(path), error_handler=handler) as physical:
        parsed = physical[0].frames[0]
        assert parsed.index_type == index_type and parsed.index == 'DEPTH'
        expected = (1000.0, 1074.75, 0.25, 'INCREASING') if known else (None,) * 4
        assert (parsed.index_min, parsed.index_max, parsed.spacing, parsed.direction) == expected
        curves = parsed.curves()
        np.testing.assert_array_equal(curves['FRAMENO'], np.arange(1, 201))
        for name, values in data.items():
            np.testing.assert_array_equal(curves[name], values[:200])
    assert not caplog.records
