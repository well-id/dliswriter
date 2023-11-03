from abc import abstractmethod

from dlis_writer.logical_record.core.logical_record import LogicalRecord
from dlis_writer.logical_record.core.logical_record_bytes import LogicalRecordBytes


class IflrAndEflrRMeta(type):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj._lr_type_struct = None
        return obj

    @property
    def lr_type_struct(cls):
        if not cls._lr_type_struct:
            cls._lr_type_struct = cls.make_lr_type_struct(cls.logical_record_type)
        return cls._lr_type_struct


class IflrAndEflrBase(LogicalRecord, metaclass=IflrAndEflrRMeta):
    is_eflr = NotImplemented
    logical_record_type = NotImplemented

    def __init__(self):
        super().__init__()

        self._bytes = None

    @abstractmethod
    def make_body_bytes(self) -> bytes:
        pass

    def represent_as_bytes(self) -> LogicalRecordBytes:
        """Writes bytes of the entire Logical Record Segment that is an EFLR object"""

        if self._bytes is None:
            bts = self._make_lrb(self.make_body_bytes())
            bts.add_header_bytes()
            self._bytes = bts

        return self._bytes

    def _make_lrb(self, bts, **kwargs):
        return super()._make_lrb(bts, lr_type_struct=self.lr_type_struct, **kwargs)

    @classmethod
    @abstractmethod
    def make_lr_type_struct(cls, lr_type):
        pass

    @property
    def lr_type_struct(self):
        return self.__class__.lr_type_struct


