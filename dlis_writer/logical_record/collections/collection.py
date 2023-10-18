from itertools import chain
from typing_extensions import Self
from configparser import ConfigParser
import logging

from dlis_writer.logical_record.collections.multi_logical_record import MultiLogicalRecord, SingleLogicalRecordWrapper
from dlis_writer.logical_record.collections.frame_data_capsule import FrameDataCapsule
from dlis_writer.logical_record.core.logical_record_base import LogicalRecordBase
from dlis_writer.logical_record.misc import StorageUnitLabel, FileHeader
from dlis_writer.logical_record.eflr_types import *


logger = logging.getLogger(__name__)


class LogicalRecordCollection(MultiLogicalRecord):
    def __init__(self, storage_unit_label: StorageUnitLabel, file_header: FileHeader, origin: Origin):
        super().__init__()

        self.storage_unit_label = storage_unit_label
        self.file_header = file_header
        self.origin = origin
        self._other_logical_records: list[MultiLogicalRecord] = []

    @property
    def other_logical_records(self):
        return self._other_logical_records

    @property
    def header_records(self):
        return self.storage_unit_label, self.file_header, self.origin

    def __len__(self):
        return len(self.header_records) + sum(len(lr) for lr in self._other_logical_records)

    def __iter__(self):
        return chain(self.header_records, *self._other_logical_records)

    def add_logical_records(self, *lrs):
        for lr in lrs:
            if isinstance(lr, MultiLogicalRecord):
                self._other_logical_records.append(lr)
            elif isinstance(lr, LogicalRecordBase):
                self._other_logical_records.append(SingleLogicalRecordWrapper(lr))
            else:
                raise TypeError(f"Expected a LogicalRecordBase or a MultiLogicalRecord instance; got {type(lr)}: {lr}")

    @staticmethod
    def make_data_records(config, data) -> FrameDataCapsule:
        frame = Frame.from_config(config)
        if frame.channels.value:
            frame.setup_channels_params_from_data(data)
            ch = f'with channels: {", ".join(c.name for c in frame.channels.value)}'
        else:
            ch = "(no channels defined)"

        logger.info(f'Preparing frames for {data.shape[0]} rows {ch}')
        data_capsule = FrameDataCapsule(frame, data)

        return data_capsule

    def _add_objects_from_config(self, config, object_class):
        cn = object_class.__name__

        objects = object_class.all_from_config(config)
        if not objects:
            logger.debug(f"No {cn}s found in the config")
        else:
            logger.info(f"Adding {cn}(s): {', '.join(p.object_name for p in objects)} to the file")
            self.add_logical_records(*objects)

    @classmethod
    def from_config(cls, config: ConfigParser, data=None) -> Self:
        obj = cls(
            storage_unit_label=StorageUnitLabel.from_config(config),
            file_header=FileHeader.from_config(config),
            origin=Origin.from_config(config)
        )

        obj._add_objects_from_config(config, Channel)

        if data is not None:
            data_capsule = cls.make_data_records(config, data)
            logger.info(f"Adding {data_capsule.frame} and FrameData objects to the file")
            obj.add_logical_records(data_capsule.frame, data_capsule.data)
        else:
            logger.warning("No data defined; adding only a Frame to the logical records")
            frame = Frame.from_config(config)
            obj.add_logical_records(frame)

        other_classes = (
            Zone,
            Parameter,
            Axis,
            Equipment,
            Tool,
            Computation,
            Process,
            Splice,
            CalibrationMeasurement,
            CalibrationCoefficient
        )

        for c in other_classes:
            obj._add_objects_from_config(config, c)

        return obj
