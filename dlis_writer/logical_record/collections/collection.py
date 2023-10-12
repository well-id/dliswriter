from itertools import chain

from dlis_writer.logical_record.collections.multi_logical_record import MultiLogicalRecord, SingleLogicalRecordWrapper
from dlis_writer.logical_record.core.logical_record_base import LogicalRecordBase
from dlis_writer.logical_record.misc import StorageUnitLabel, FileHeader
from dlis_writer.logical_record.eflr_types import Origin


class LogicalRecordCollection(MultiLogicalRecord):
    def __init__(self, storage_unit_label: StorageUnitLabel, file_header: FileHeader, origin: Origin):
        super().__init__()

        self.storage_unit_label = storage_unit_label
        self.file_header = file_header
        self.origin = origin
        self._other_logical_records: list[MultiLogicalRecord] = []

    @property
    def header_records(self):
        return self.storage_unit_label, self.file_header, self.origin

    def __len__(self):
        return len(self.header_records) + sum(len(lr) for lr in self._other_logical_records)

    def __iter__(self):
        return chain(self.header_records, self._other_logical_records)

    def add_logical_record(self, lr):
        if isinstance(lr, MultiLogicalRecord):
            self._other_logical_records.append(lr)
        elif isinstance(lr, LogicalRecordBase):
            self._other_logical_records.append(SingleLogicalRecordWrapper(lr))
        else:
            raise TypeError(f"Expected a LogicalRecordBase or a MultiLogicalRecord instance; got {type(lr)}: {lr}")
