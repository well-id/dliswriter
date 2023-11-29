from abc import abstractmethod
import logging
from typing import Union

from dlis_writer.logical_record.core.logical_record.logical_record_bytes import LogicalRecordBytes
from dlis_writer.utils.enums import RepresentationCode, EFLRType, IFLRType
from dlis_writer.utils.struct_writer import write_struct


logger = logging.getLogger(__name__)


class LRMeta(type):
    """Define a metaclass for all logical records.

    This metaclass adds a class-level property 'lr_type_struct' to LogicalRecord. This allows the value to be computed
    once for each LogicalRecord subclass.
    """

    def __new__(cls, *args, **kwargs):
        """Create a new LogicalRecord (sub)class.

        Add a class-level attribute _lr_type_struct to be set when the value is first accessed through the corresponding
        property.
        """

        obj = super().__new__(cls, *args, **kwargs)
        obj._lr_type_struct = None
        return obj

    @property
    def lr_type_struct(cls) -> bytes:
        """Bytes describing the type of the logical record."""

        if not cls._lr_type_struct:
            cls._lr_type_struct = write_struct(RepresentationCode.USHORT, cls.logical_record_type.value)
        return cls._lr_type_struct


class LogicalRecord(metaclass=LRMeta):
    """Create a base for all logical record classes."""

    is_eflr = NotImplemented  #: indication whether this is an explicitly or indirectly formatted LR
    logical_record_type: Union[EFLRType, IFLRType] = NotImplemented  #: int-enum denoting type of the logical record

    def __init__(self, *args, **kwargs):
        """Initialise a LogicalRecord."""

        pass

    @abstractmethod
    def _make_body_bytes(self) -> bytes:
        """Create bytes describing the body of this LogicalRecord.

        See the implementations subclasses: EFLR, FrameData (IFLR), and NoFormatFrameData (IFLR).
        """

        pass

    def represent_as_bytes(self) -> LogicalRecordBytes:
        """Create bytes representing the LogicalRecord.

        The bytes are wrapped in LogicalRecordBytes object which facilitates dividing the array of bytes into segments
        which can fit into visible records (physical units of DLIS).
        """

        return LogicalRecordBytes(
            self._make_body_bytes(),
            lr_type_struct=self.__class__.lr_type_struct,
            is_eflr=self.is_eflr
        )
