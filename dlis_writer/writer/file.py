from typing import Any, Union, Optional, Callable
import numpy as np
import os
from timeit import timeit
from datetime import timedelta
import logging

from dlis_writer.utils.enums import RepresentationCode as RepC
from dlis_writer.utils.source_data_objects import DictInterface
from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.logical_record.core.eflr import EFLRObject
from dlis_writer.logical_record.eflr_types.origin import OriginObject, Origin
from dlis_writer.logical_record.eflr_types.file_header import FileHeaderObject, FileHeader
from dlis_writer.logical_record.eflr_types.axis import AxisObject, Axis
from dlis_writer.logical_record.eflr_types.channel import ChannelObject, Channel
from dlis_writer.logical_record.eflr_types.frame import FrameObject, Frame
from dlis_writer.logical_record.collections.file_logical_records import FileLogicalRecords
from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.writer.writer import DLISWriter


logger = logging.getLogger(__name__)


kwargs_type = dict[str, Any]


class DLISFile:
    def __init__(
            self,
            storage_unit_label: Optional[Union[StorageUnitLabel, kwargs_type]] = None,
            file_header: Optional[Union[FileHeaderObject, kwargs_type]] = None,
            origin: Optional[Union[OriginObject, kwargs_type]] = None
    ):

        if isinstance(storage_unit_label, StorageUnitLabel):
            self._sul = storage_unit_label
        else:
            self._sul = StorageUnitLabel(**({"set_identifier": "MAIN STORAGE UNIT"} | (storage_unit_label or {})))

        if isinstance(file_header, FileHeaderObject):
            self._file_header = file_header
        else:
            self._file_header = FileHeader.make_object(**({"name": "FILE HEADER"} | (file_header or {})))

        if isinstance(origin, OriginObject):
            self._origin = origin
        else:
            self._origin = Origin.make_object(**({"name": "ORIGIN", "file_set_number": 1} | (origin or {})))

        self._channels = []
        self._frames = []
        self._other = []

        self._data_dict = {}

    @property
    def storage_unit_label(self) -> StorageUnitLabel:
        return self._sul

    @property
    def file_header(self) -> FileHeaderObject:
        return self._file_header

    @property
    def origin(self) -> OriginObject:
        return self._origin

    @property
    def channels(self) -> list[ChannelObject]:
        return self._channels

    @property
    def frames(self) -> list[FrameObject]:
        return self._frames

    def add_channel(
            self,
            name: str,
            data: np.ndarray,
            dataset_name: str = None,
            long_name: Optional[str] = None,
            properties: Optional[list[str]] = None,
            representation_code: RepC = None,
            units: Optional[str] = None,
            axis: Optional[AxisObject] = None,
            minimum_value: Optional[float] = None,
            maximum_value: Optional[float] = None
    ) -> ChannelObject:

        if not isinstance(data, np.ndarray):
            raise ValueError(f"Expected a numpy.ndarray, got a {type(data)}")

        ch = Channel.make_object(
            name,
            dataset_name=dataset_name,
            long_name=long_name,
            properties=properties,
            representation_code=representation_code,
            units=units,
            axis=axis,
            minimum_value=minimum_value,
            maximum_value=maximum_value
        )
        # skipping dimension and element_limit because they will be determined from the data

        self._channels.append(ch)
        self._data_dict[ch.dataset_name] = data  # channel's dataset_name is the provided dataset_name or channel's name

        return ch

    def add_frame(self, name, channels: Union[list[ChannelObject], tuple[ChannelObject, ...]], **kwargs):
        if not isinstance(channels, (list, tuple)):
            raise TypeError(f"Expected a list or tuple of channels, got {type(channels)}: {channels}")

        if not channels:
            raise ValueError("At least one channel must be specified for a frame")

        if not all(isinstance(c, ChannelObject) for c in channels):
            raise TypeError(f"Expected a list of ChannelObject instances; "
                            f"got types: {', '.join(str(type(c)) for c in channels)}")

        fr = Frame.make_object(name, channels=channels, **kwargs)
        self._frames.append(fr)
        return fr

    def _make_multi_frame_data(self, fr: FrameObject, **kwargs):
        name_mapping = {ch.name: ch.dataset_name for ch in fr.channels.value}
        data_object = DictInterface(self._data_dict, mapping=name_mapping)
        fr.setup_from_data(data_object)
        return MultiFrameData(fr, data_object, **kwargs)

    def make_file_logical_records(self, chunk_size: Optional[int] = None):

        flr = FileLogicalRecords(
            sul=self._sul,
            fh=self._file_header.parent,
            orig=self._origin.parent
        )

        def get_parents(objects):
            return set(obj.parent for obj in objects)

        flr.add_channels(*get_parents(self._channels))
        flr.add_frames(*get_parents(self._frames))
        flr.add_frame_data_objects(*(self._make_multi_frame_data(fr, chunk_size=chunk_size) for fr in self._frames))

        return flr

    def write(self, dlis_file_name: Union[str, os.PathLike[str]], visible_record_length: int = 8192,
              input_chunk_size: Optional[int] = None, output_chunk_size: Union[int, float] = 2**32):
        """Create a DLIS file form the current specifications.

        Args:
            dlis_file_name          :   Name of the file to be created.
            visible_record_length   :   Maximal length of visible records to be created in the file.
            input_chunk_size        :   Size of the chunks (in rows) in which input data will be loaded to be processed.
            output_chunk_size       :   Size of the buffers accumulating file bytes before file write action is called.

        """

        def timed_func():
            """Perform the action of creating a DLIS file.

            This function is used in a timeit call to time the file creation.
            """

            dlis_file = DLISWriter(visible_record_length=visible_record_length)
            logical_records = self.make_file_logical_records(chunk_size=input_chunk_size)
            dlis_file.create_dlis(logical_records, filename=dlis_file_name, output_chunk_size=output_chunk_size)

        exec_time = timeit(timed_func, number=1)
        logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")


if __name__ == '__main__':
    orig = Origin.make_object("DEFAULT ORIGIN", file_set_number=1, company="XXX")
    df = DLISFile(origin=orig, file_header={'sequence_number': 2})
    df.origin.order_number.value = "352"

    size = 100
    ch1 = df.add_channel('DEPTH', data=np.arange(size)/10, units='m')
    ch2 = df.add_channel("RPM", data=(np.arange(size) % 10).astype(float))
    ch3 = df.add_channel("AMPLITUDE", data=np.random.rand(size, 5))
    main_frame = df.add_frame("MAIN FRAME", channels=(ch1, ch2, ch3), index_type='BOREHOLE-DEPTH')

    df.write('./tmp.DLIS', input_chunk_size=20)
