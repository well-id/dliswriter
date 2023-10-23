from itertools import chain
from typing_extensions import Self
from configparser import ConfigParser
import logging
from functools import reduce

from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.logical_record.collections.multi_logical_record import MultiLogicalRecord
from dlis_writer.logical_record.misc import StorageUnitLabel, FileHeader
from dlis_writer.logical_record.eflr_types import *
from dlis_writer.logical_record.core.eflr import EFLR


logger = logging.getLogger(__name__)


class LogicalRecordCollection(MultiLogicalRecord):
    def __init__(self, storage_unit_label: StorageUnitLabel, file_header: FileHeader, origin: Origin):
        super().__init__()

        self.storage_unit_label = storage_unit_label
        self.file_header = file_header
        self.origin = origin
        self._channels: list[Channel] = []
        self._frames: list[Frame] = []
        self._frame_data_objects: list[MultiFrameData] = []
        self._other_logical_records: list[EFLR] = []

    def set_origin_reference(self, value):
        self.file_header.origin_reference = value
        self.origin.origin_reference = value

        for iterable in (self._channels, self._frames, self._frame_data_objects):
            for ob in iterable:
                ob.origin_reference = value

        for lr in self._other_logical_records:
            lr.origin_reference = value

    @property
    def other_logical_records(self):
        return self._other_logical_records

    @property
    def header_records(self):
        return self.storage_unit_label, self.file_header, self.origin

    @staticmethod
    def _check_type_of_values(values, expected_type):
        if not all(isinstance(v, expected_type) for v in values):
            raise TypeError(f"Expected only {expected_type.__name__} objects; "
                            f"got {', '.join(type(v).__name__ for v in values)}")

    @property
    def channels(self) -> list[Channel]:
        if self._channels:
            return self._channels

        all_channels_from_frames = [fdc.channels for fdc in self._frames]
        if all_channels_from_frames:
            return reduce(lambda a, b: a + b, all_channels_from_frames)
        return []

    def add_channels(self, *channels):
        self._check_type_of_values(channels, Channel)
        self._channels.extend(channels)

    @property
    def frames(self):
        return self._frames

    def add_frames(self, *frames):
        self._check_type_of_values(frames, Frame)
        self._frames.extend(frames)

    @property
    def frame_data_objects(self):
        return self._frame_data_objects

    def add_frame_data_objects(self, *fds):
        self._check_type_of_values(fds, MultiFrameData)
        self._frame_data_objects.extend(fds)

    def __len__(self):
        other_len = len(self._other_logical_records)
        len_data = sum(len(mfd) for mfd in self.frame_data_objects)
        return len(self.header_records) + len(self.channels) + len(self.frames) + len_data + other_len

    def __iter__(self):
        return chain(
            self.header_records,  # tuple of EFLRs
            self.channels,  # list of channels
            self.frames,  # list of frames
            *self.frame_data_objects,  # list of iterables - MultiFrameData objects
            self._other_logical_records  # list of EFLRs
        )

    def add_logical_records(self, *lrs):
        self._check_type_of_values(lrs, EFLR)
        self._other_logical_records.extend(lrs)

    @staticmethod
    def make_frame_and_data(config, data):
        frame = Frame.make_from_config(config)
        if frame.channels.value:
            frame.setup_from_data(data)
            ch = f'with channels: {", ".join(c.name for c in frame.channels.value)}'
        else:
            ch = "(no channels defined)"

        logger.info(f'Preparing frames for {data.shape[0]} rows {ch}')
        multi_frame_data = MultiFrameData(frame, data)

        return frame, multi_frame_data

    def _add_objects_from_config(self, config, object_class):
        cn = object_class.__name__

        objects = object_class.get_or_make_all_from_config(config)
        if not objects:
            logger.debug(f"No {cn}s found in the config")
        else:
            logger.info(f"Adding {cn}(s): {', '.join(p._name for p in objects)} to the file")
            self.add_logical_records(*objects)

    @classmethod
    def from_config_and_data(cls, config: ConfigParser, data) -> Self:
        obj = cls(
            storage_unit_label=StorageUnitLabel.make_from_config(config),
            file_header=FileHeader.make_from_config(config),
            origin=Origin.make_from_config(config)
        )

        channels = Channel.get_or_make_all_from_config(config)
        frame, multi_frame_data = cls.make_frame_and_data(config, data)

        logger.info(f"Adding Channels: {', '.join(ch.name for ch in channels)} to the file")
        obj.add_channels(*channels)
        logger.info(f"Adding {frame} and {len(multi_frame_data)} FrameData objects to the file")
        obj.add_frames(frame)
        obj.add_frame_data_objects(multi_frame_data)

        other_classes = [c for c in eflr_types if c not in (Channel, Frame, Origin)]

        for c in other_classes:
            c.get_or_make_all_from_config(config)

        # the division into the two loops is on purpose
        # we first make all instances, then add all instances from all classes
        # in case some are added in non-standard order
        for c in other_classes:
            inst = c.get_all_instances()
            if not inst:
                logger.debug(f"No instances of {c.__name__} defined")
            else:
                logger.info(f"Adding {c.__name__}(s): {', '.join(p._name for p in inst)} to the file")
                obj.add_logical_records(*inst)

        return obj
