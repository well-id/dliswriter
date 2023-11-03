from abc import abstractmethod
from functools import cached_property
import numpy as np

from line_profiler_pycharm import profile

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.logical_record_base import LogicalRecord, LogicalRecordBytes
from dlis_writer.logical_record.core.segment_attributes import SegmentAttributes


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

    @classmethod
    def make_lr_type_struct(cls, logical_record_type):
        return write_struct(RepresentationCode.USHORT, logical_record_type.value)


class IflrAndEflrBase(LogicalRecord, metaclass=IflrAndEflrRMeta):
    is_eflr = NotImplemented
    logical_record_type = NotImplemented

    def __init__(self):
        super().__init__()

        self.segment_attributes = SegmentAttributes()
        self.segment_attributes.is_eflr = self.is_eflr

        self._bytes = None

    @abstractmethod
    def make_body_bytes(self) -> bytes:
        pass

    def _make_segment_attributes(self, **kwargs) -> bytes:
        """Writes the logical record segment attributes.

        .._RP66 V1 Logical Record Segment Header:
            http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1

        """

        return write_struct(RepresentationCode.USHORT, self.segment_attributes.reduce(**kwargs))

    @cached_property
    def size(self) -> int:
        """Calculates the size of the Logical Record Segment"""

        return self.represent_as_bytes().size

    def represent_as_bytes(self) -> LogicalRecordBytes:
        """Writes bytes of the entire Logical Record Segment that is an EFLR object"""

        if self._bytes is None:
            bts = self.make_body_bytes()
            bts = self.make_header_bytes(bts) + bts
            if self.segment_attributes.has_padding:
                bts += write_struct(RepresentationCode.USHORT, 1)

            self._bytes = LogicalRecordBytes(bts)

        return self._bytes

    def make_header_bytes(self, bts: bytes) -> bytes:
        """Writes Logical Record Segment Header

        .._RP66 V1 Logical Record Segment Header:
            http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1

        """
        segment_length = len(bts) + 4
        if segment_length % 2 != 0:
            segment_length += 1
            self.segment_attributes.has_padding = True
        else:
            self.segment_attributes.has_padding = False

        return write_struct(RepresentationCode.UNORM, segment_length) \
            + self._make_segment_attributes() \
            + self.lr_type_struct

    @profile
    def split(self, segment_length: int, is_first: bool = False, is_last: bool = False) -> bytes:
        """Creates header bytes to be inserted into split position

        When a Logical Record Segment overflows a Visible Record, it must be split.
        A split operation involves:
            1. Changing the header of the first part of the split
            2. Adding a header to the second part of the split

        Args:
            is_first: Represents whether this is the first part of the split
            is_last: Represents whether this is the last part of the split
            segment_length: Length of the segment after split operation

        Returns:
            Header bytes to be inserted into split position

        """

        assert segment_length % 2 == 0, 'Split segment length is not an EVEN NUMBER'
        assert segment_length < self.size, 'Split segment length can not be larger than the whole segment'

        self.segment_attributes.mark_order(first=is_first, last=is_last)

        _attributes = self._make_segment_attributes(no_padding=is_first)

        return write_struct(RepresentationCode.UNORM, segment_length) + _attributes + self.lr_type_struct

    @classmethod
    @abstractmethod
    def make_lr_type_struct(cls, lr_type):
        pass

    @property
    def lr_type_struct(self):
        return self.__class__.lr_type_struct


