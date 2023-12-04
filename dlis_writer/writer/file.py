from typing import Any, Union
import numpy as np

from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.logical_record.eflr_types import *
from dlis_writer.logical_record.eflr_types.channel import ChannelObject
from dlis_writer.logical_record.collections.file_logical_records import FileLogicalRecords


class DLISFile:
    def __init__(self):
        self._sul = None
        self._file_header = None
        self._origin = None

        self._channels = []
        self._frames = []
        self._multi_frame_data = []
        self._other = []

        self._data_dict = {}

    @staticmethod
    def _check_already_defined(obj: Any):
        if obj is not None:
            raise RuntimeError(f"{obj.__class__.__name__} is already defined in the file")

    def add_storage_unit_label(self, *args, **kwargs):
        self._check_already_defined(self._sul)
        self._sul = StorageUnitLabel(*args, **kwargs)
        return self._sul

    def add_file_header(self, *args, **kwargs):
        self._check_already_defined(self._file_header)
        self._file_header = FileHeader.make_object(*args, **kwargs)
        return self._file_header

    def add_origin(self, *args, **kwargs):
        self._check_already_defined(self._origin)
        self._origin = Origin.make_object(*args, **kwargs)
        return self._origin

    def add_channel(self, name, data, **kwargs) -> ChannelObject:
        if not isinstance(data, np.ndarray):
            raise ValueError(f"Expected a numpy.ndarray, got a {type(data)}")

        ch = Channel.make_object(name, **kwargs)
        self._channels.append(ch)

        dataset_name = kwargs.get('dataset_name', name)
        self._data_dict[dataset_name] = data

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

    def make_file_logical_records(self):
        req = {
            "Storage Unit Label": self._sul,
            "File Header": self._file_header,
            "Origin": self._origin
        }

        missing = [k for k, v in req.items() if v is None]
        if any(missing):
            raise RuntimeError(f"Required records not defined: {', '.join(missing)}")

        flr = FileLogicalRecords(
            sul=self._sul,
            fh=self._file_header.parent,
            orig=self._origin.parent
        )

        def get_parents(objects):
            return set(obj.parent for obj in objects)

        flr.add_channels(*get_parents(self._channels))
        flr.add_frames(*get_parents(self._frames))

        return flr


if __name__ == '__main__':
    df = DLISFile()
    df.add_storage_unit_label("DEFAULT STORAGE SET", sequence_number=1)
    df.add_file_header("DEFAULT FILE HEADER", sequence_number=1)
    df.add_origin("DEFAULT ORIGIN", file_set_number=1)

    size = 20
    ch1 = df.add_channel("Channel 1", data=np.arange(size))
    ch2 = df.add_channel("amplitude", data=np.random.rand(size, 5))
    main_frame = df.add_frame("MAIN FRAME", channels=(ch1, ch2))

    records = df.make_file_logical_records()
