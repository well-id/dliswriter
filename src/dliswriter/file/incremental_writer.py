"""Fixed-schema Frame Data writing within one process lifetime."""

from pathlib import Path
from tempfile import SpooledTemporaryFile
from types import TracebackType
from typing import Optional, TYPE_CHECKING, Union

import h5py  # type: ignore  # untyped library
import numpy as np

from dliswriter.file.multi_frame_data import MultiFrameData
from dliswriter.file.writer import DLISWriter
from dliswriter.logical_record.eflr_types.channel import ChannelItem
from dliswriter.logical_record.iflr_types import FrameData
from dliswriter.utils.internal.converters import ReprCodeConverter
from dliswriter.utils.internal.struct_writer import write_struct_uvari
from dliswriter.utils.internal.types import data_form_type, file_name_type
from dliswriter.utils.source_data_wrappers import (
    DictDataWrapper, NumpyDataWrapper, SourceDataWrapper,
)

if TYPE_CHECKING:
    from dliswriter.file.file import DLISFile


# Bound the additional prepared representation independently of the output setting.
# Rollover occurs after a write, so transient spool storage can exceed this by one VR.
_PREPARED_MAX_SIZE = 2**20


class IncrementalDLISWriter:
    """Write one Logical File / Frame with frozen metadata and safe numeric casts.

    Use ``DLISFile.start_incremental`` to start a session. Each batch is fully
    prepared before emission. Validation errors permit retry; emission errors
    permanently prohibit further appends. No recovery or rollback is provided.
    """

    def __init__(self, definition: 'DLISFile', filename: file_name_type,
                 initial_data: data_form_type, output_chunk_size: int = 2**20) -> None:
        self._closed = False
        self._failed = False
        self._next_frame_number = 1
        if len(definition.logical_files) != 1:
            raise ValueError('Incremental writing requires exactly one Logical File')
        lf = definition.logical_files[0]
        if len(lf.frames) != 1:
            raise ValueError('Incremental writing requires exactly one Frame')
        if lf._no_format_frame_data:
            raise ValueError('NoFormat data is not supported by incremental writing')
        if isinstance(output_chunk_size, bool) or not isinstance(output_chunk_size, int):
            raise TypeError('output_chunk_size must be an integer')
        path = Path(filename).absolute()
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)

        frozen = definition._snapshot_metadata()
        frozen_lf = frozen.logical_files[0]
        self._frame = frozen_lf.frames[0]
        channels = self._frame.channels.value or []
        if (not channels or len(set(channels)) != len(channels)
                or set(channels) != set(frozen_lf.channels)
                or len({ch.name for ch in channels}) != len(channels)
                or len({ch.dataset_name for ch in channels}) != len(channels)):
            raise ValueError('Frame must contain every registered channel exactly once with unique names/mapping')
        self._writer = DLISWriter(path, frozen.storage_unit_label.max_record_length)
        self._writer._check_output_chunk_size(output_chunk_size)
        self._output_chunk_size = output_chunk_size
        self._row_shapes: dict[str, tuple[int, ...]] = {}
        records = self._prepare(initial_data, infer=True)
        frozen_lf.check_objects()
        self._emit(records, frozen=frozen)

    def _read_source(self, batch: data_form_type) -> Union[dict[str, np.ndarray], np.ndarray]:
        """Load selected HDF5 arrays with deterministic handle cleanup."""
        if isinstance(batch, dict):
            DictDataWrapper._check_source_dict(batch)
            return batch
        if isinstance(batch, np.ndarray):
            NumpyDataWrapper._check_source_arr(batch)
            if batch.ndim != 1:
                raise ValueError('Structured source must be one-dimensional')
            return batch
        path = Path(batch)
        if path.suffix.lower() not in ('.h5', '.hdf5'):
            raise ValueError('Expected a dictionary, structured array or HDF5 path')
        # Use an owned context rather than the existing HDF5 wrapper constructor:
        # its failure cleanup relies on finalization of a partially built object.
        with h5py.File(path, 'r') as source:
            return {name: source[name][:] for name in self._frame.channel_name_mapping.values()}

    def _infer_channel_structure(self, channel: ChannelItem, shape: tuple[int, ...], target: np.dtype) -> None:
        """Fill missing structure while preserving consistent explicit attributes."""
        name = channel.name
        dimension = list(shape) or [1]
        repr_code = ReprCodeConverter.determine_repr_code_from_numpy_dtype(target)
        if channel.dimension.value is not None and channel.dimension.value != dimension:
            raise ValueError(f'{name}: dimension does not match initial data')
        if (channel.representation_code.value is not None
                and channel.representation_code.value != repr_code):
            raise ValueError(f'{name}: representation code does not match dtype')
        channel.dimension.value = dimension
        if channel.element_limit.value is None:
            channel.element_limit.value = dimension
        if not channel._compare_element_limit_vs_dimension(channel.element_limit.value, dimension):
            raise ValueError(f'{name}: element limit does not contain dimension')
        channel.cast_dtype = target
        self._row_shapes[name] = shape

    def _prepare(self, batch: data_form_type, infer: bool = False) -> list[FrameData]:
        source = self._read_source(batch)
        normalized = {}
        lengths = set()
        for channel in self._frame.channels.value:
            name = channel.name
            try:
                values = source[channel.dataset_name]
            except (KeyError, ValueError) as exc:
                raise ValueError(f'Missing dataset {channel.dataset_name!r}') from exc
            if values.ndim not in (1, 2) or not values.shape[0] or any(n < 1 for n in values.shape):
                raise ValueError(f'{name}: expected positive rows of scalar or vector samples')
            lengths.add(values.shape[0])
            shape = values.shape[1:]
            ReprCodeConverter.validate_numpy_dtype(values.dtype)
            target = np.dtype(channel.cast_dtype if channel.cast_dtype is not None else values.dtype).newbyteorder('=')
            if not np.can_cast(values.dtype, target, casting='safe'):
                raise ValueError(f'{name}: unsafe cast from {values.dtype} to {target}')
            if infer:
                self._infer_channel_structure(channel, shape, target)
            elif shape != self._row_shapes[name]:
                raise ValueError(f'{name}: sample shape differs from frozen schema')
            # Native-endian numeric values are required by FrameData's byte swap.
            normalized[name] = values.astype(target, casting='safe', copy=True)
        if len(lengths) != 1:
            raise ValueError('All selected channels must have equal positive lengths')
        self._frame._validate_index_structure(normalized[self._frame.channels.value[0].name].ndim)
        n_rows = lengths.pop()
        # Delegate the representable counter boundary to the existing UVARI codec.
        write_struct_uvari(self._next_frame_number + n_rows - 1)
        wrapper = SourceDataWrapper.make_wrapper(normalized, mapping={name: name for name in normalized})
        return list(MultiFrameData(self._frame, wrapper, first_frame_number=self._next_frame_number))

    def _emit(self, records: list[FrameData], frozen: Optional['DLISFile'] = None) -> None:
        """Prepare once, then commit exactly the retained bytes without serializers."""
        commit_started = False
        try:
            with SpooledTemporaryFile(max_size=_PREPARED_MAX_SIZE, mode='w+b') as prepared:
                if frozen is not None:
                    prepared.write(frozen.storage_unit_label.represent_as_bytes().bts)
                    for visible_record in self._writer._iter_visible_records(frozen.generator([[]])):
                        prepared.write(visible_record)
                for visible_record in self._writer._iter_visible_records(records):
                    prepared.write(visible_record)
                prepared.seek(0)
                commit_started = True
                self._writer._commit_prepared(
                    prepared, min(self._output_chunk_size, _PREPARED_MAX_SIZE), includes_sul=frozen is not None,
                )
        except BaseException:
            # Cleanup can itself fail after a successful copy. Conservatively
            # poison then too: bytes may exist, but this call did not complete.
            if commit_started:
                self._failed = True
            raise
        self._next_frame_number += len(records)

    def append(self, batch: data_form_type) -> None:
        """Append only FDATA, preserving the frozen schema and continuous numbering."""
        if self._closed:
            raise RuntimeError('Incremental writer is closed')
        if self._failed:
            raise RuntimeError('Incremental writer failed during emission; cannot append')
        self._emit(self._prepare(batch))

    def close(self) -> None:
        """End the session without writing records; repeated calls are harmless."""
        self._closed = True

    def __enter__(self) -> 'IncrementalDLISWriter':
        if self._closed or self._failed:
            raise RuntimeError('Incremental writer is closed or failed')
        return self

    def __exit__(self, exc_type: Optional[type[BaseException]], exc_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        self.close()
