from itertools import chain
from typing_extensions import Self
from configparser import ConfigParser
import logging

from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.logical_record.collections.multi_logical_record import MultiLogicalRecord
from dlis_writer.logical_record.misc import StorageUnitLabel, FileHeader
from dlis_writer.logical_record.eflr_types import *
from dlis_writer.logical_record.eflr_types.frame import FrameObject
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
        def get_len(lr_list):
            return sum(lr.n_objects for lr in lr_list)

        len_channels = get_len(self._channels)
        len_frames = get_len(self._frames)
        len_other = get_len(self._other_logical_records)
        len_data = sum(len(mfd) for mfd in self.frame_data_objects)
        return len(self.header_records) + len_channels + len_frames + len_data + len_other

    def __iter__(self):
        return chain(
            self.header_records,  # tuple of EFLRs
            self._channels,  # list of channels
            self._frames,  # list of frames
            self.frame_data_objects,  # list of iterables - MultiFrameData objects
            self._other_logical_records  # iterable of lists of EFLRs
        )

    def add_logical_records(self, *lrs):
        self._check_type_of_values(lrs, EFLR)
        self._other_logical_records.extend(lrs)

    def check_objects(self):
        def verify_n(names, class_name, exactly_one=False):
            n = len(names)
            if not n:
                raise RuntimeError(f"No {class_name}Object defined")

            if exactly_one and n > 1:
                raise RuntimeError(f"Expected exactly one {class_name}Object, got {n} with names: "
                                   f"{', '.join(repr(n) for n in names)}")

        def check(eflr, exactly_one=False):
            names = [o.name for o in eflr.get_all_objects()]
            verify_n(names, eflr.__class__.__name__, exactly_one=exactly_one)

        def check_list(eflr_list, class_name):
            names = []
            for eflr in eflr_list:
                names.extend(o.name for o in eflr.get_all_objects())
            verify_n(names, class_name)

        check(self.file_header, exactly_one=True)
        check(self.origin)
        check_list(self.frames, "Frame")
        check_list(self._channels, "Channel")

    @staticmethod
    def make_frame_and_data(config, data, key='Frame'):
        frame_object: FrameObject = Frame.make_object_from_config(config, key=key)
        if frame_object.channels.value:
            frame_object.setup_from_data(data)
            ch = f'with channels: {", ".join(c.name for c in frame_object.channels.value)}'
        else:
            ch = "(no channels defined)"

        logger.info(f'Preparing frames for {data.shape[0]} rows {ch}')
        multi_frame_data = MultiFrameData(frame_object, data)

        return frame_object, multi_frame_data

    def _add_objects_from_config(self, config, object_class):
        cn = object_class.__name__

        objects = object_class.make_all_objects_from_config(config, get_if_exists=True)
        if not objects:
            logger.debug(f"No {cn}s found in the config")
        else:
            logger.info(f"Adding {cn}(s): {', '.join(p.name for p in objects)} to the file")
            self.add_logical_records(*objects)

    @classmethod
    def from_config_and_data(cls, config: ConfigParser, data) -> Self:
        file_header_object = FileHeader.make_object_from_config(config)
        origin_object = Origin.make_object_from_config(config)

        obj = cls(
            storage_unit_label=StorageUnitLabel.make_from_config(config),
            file_header=file_header_object.parent,
            origin=origin_object.parent
        )

        channels = Channel.make_all_objects_from_config(config)

        frame_keys = (key for key in config.sections() if key.startswith('Frame-') or key == 'Frame')
        frame_and_data_objects = [cls.make_frame_and_data(config, data, key=key) for key in frame_keys]

        logger.info(f"Adding Channels: {', '.join(ch.name for ch in channels)} to the file")
        obj.add_channels(*(set(c.parent for c in channels)))

        for frame, multi_frame_data in frame_and_data_objects:
            logger.info(f"Adding {frame} and {len(multi_frame_data)} FrameData objects to the file")
            if frame.parent not in obj.frames:
                obj.add_frames(frame.parent)
            obj.add_frame_data_objects(multi_frame_data)

        other_classes = [c for c in eflr_types if c not in (Channel, Frame, Origin)]

        for c in other_classes:
            objects = c.make_all_objects_from_config(config, get_if_exists=True)
            if not objects:
                logger.debug(f"No instances of {c.__name__} defined")
            else:
                logger.info(f"Adding {c.__name__}(s): {', '.join(o.name for o in objects)} to the file")
                obj.add_logical_records(*set(o.parent for o in objects))

        return obj
