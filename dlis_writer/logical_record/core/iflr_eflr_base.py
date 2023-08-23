from abc import abstractmethod
from functools import lru_cache
from line_profiler_pycharm import profile

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.logical_record_base import LogicalRecordBase


class IflrAndEflrBase(LogicalRecordBase):
    is_eflr = NotImplemented

    def __init__(self):
        self.logical_record_type = None

        self.has_predecessor_segment = False
        self.has_successor_segment = False
        self.is_encrypted = False
        self.has_encryption_protocol = False
        self.has_checksum = False
        self.has_trailing_length = False
        self.has_padding = False

    @property
    @abstractmethod
    def body_bytes(self):
        pass

    @property
    def segment_attributes(self) -> bytes:
        """Writes the logical record segment attributes.

        .._RP66 V1 Logical Record Segment Header:
            http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1

        """
        _bits = str(int(self.is_eflr)) \
                + str(int(self.has_predecessor_segment)) \
                + str(int(self.has_successor_segment)) \
                + str(int(self.is_encrypted)) \
                + str(int(self.has_encryption_protocol)) \
                + str(int(self.has_checksum)) \
                + str(int(self.has_trailing_length)) \
                + str(int(self.has_padding))

        return write_struct(RepresentationCode.USHORT, int(_bits, 2))

    @property
    def size(self) -> int:
        """Calculates the size of the Logical Record Segment"""

        return len(self.represent_as_bytes())

    @lru_cache()
    @profile
    def represent_as_bytes(self):
        """Writes bytes of the entire Logical Record Segment that is an EFLR object"""

        self.bytes = b''
        self.bytes += self.body_bytes
        self.bytes = self.header_bytes + self.bytes
        if self.has_padding:
            self.bytes += write_struct(RepresentationCode.USHORT, 1)

        return self.bytes

    @property
    @abstractmethod
    def header_bytes(self) -> bytes:
        pass

    def split(self, is_first: bool, is_last: bool, segment_length: int, add_extra_padding: bool) -> bytes:
        """Creates header bytes to be inserted into split position

        When a Logical Record Segment overflows a Visible Record, it must be split.
        A split operation involves:
            1. Changing the header of the first part of the split
            2. Adding a header to the second part of the split

        Args:
            is_first: Represents whether this is the first part of the split
            is_last: Represents whether this is the last part of the split
            segment_length: Length of the segment after split operation
            add_extra_padding: If after the split the segment length is smaller than 16
                adds extra padding to comply with the minimum length.

        Returns:
            Header bytes to be inserted into split position

        """

        assert int(is_first) + int(is_last) != 2, 'Split segment can not be both FIRST and LAST'
        assert segment_length % 2 == 0, 'Split segment length is not an EVEN NUMBER'
        assert segment_length < self.size, 'Split segment length can not be larger than the whole segment'

        _length = write_struct(RepresentationCode.UNORM, segment_length)

        toggle_padding = False

        if is_first:
            self.has_predecessor_segment = False
        else:
            self.has_predecessor_segment = True

        if is_last:
            self.has_successor_segment = False
        else:
            self.has_successor_segment = True
            if self.has_padding is not add_extra_padding:
                toggle_padding = True
                self.has_padding = not self.has_padding

        _attributes = self.segment_attributes

        if toggle_padding:
            self.has_padding = not self.has_padding

        return _length + _attributes + self._write_struct_for_lr_type()

    def __repr__(self):
        """String representation of this object"""
        return self.set_type

    @abstractmethod
    def _write_struct_for_lr_type(self):
        pass
