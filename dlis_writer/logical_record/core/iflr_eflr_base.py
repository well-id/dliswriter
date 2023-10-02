from abc import abstractmethod
from functools import cached_property
import numpy as np

from line_profiler_pycharm import profile

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.logical_record_base import LogicalRecordBase


class SegmentAttributes:
    weights = [2 ** i for i in range(8)][::-1]

    def __init__(self):
        self._value = 8 * [False]

    @property
    def is_eflr(self):
        return self._value[0]

    @is_eflr.setter
    def is_eflr(self, b):
        self._value[0] = b

    @property
    def has_predecessor_segment(self):
        return self._value[1]

    @has_predecessor_segment.setter
    def has_predecessor_segment(self, b):
        self._value[1] = b

    @property
    def has_successor_segment(self):
        return self._value[2]

    @has_successor_segment.setter
    def has_successor_segment(self, b):
        self._value[2] = b

    @property
    def is_encrypted(self):
        return self._value[3]

    @is_encrypted.setter
    def is_encrypted(self, b):
        self._value[3] = b

    @property
    def has_encryption_protocol(self):
        return self._value[4]

    @has_encryption_protocol.setter
    def has_encryption_protocol(self, b):
        self._value[4] = b

    @property
    def has_checksum(self):
        return self._value[5]

    @has_checksum.setter
    def has_checksum(self, b):
        self._value[5] = b

    @property
    def has_trailing_length(self):
        return self._value[6]

    @has_trailing_length.setter
    def has_trailing_length(self, b):
        self._value[6] = b

    @property
    def has_padding(self):
        return self._value[7]

    @has_padding.setter
    def has_padding(self, b):
        self._value[7] = b

    def toggle_padding(self):
        self._value[7] = not self._value[7]

    def reduce(self):
        return sum(map(lambda x, y: x * y, self._value, self.weights))


class IflrAndEflrBase(LogicalRecordBase):
    is_eflr = NotImplemented
    lr_type_struct = NotImplemented

    def __init__(self):
        self.segment_attributes = SegmentAttributes()
        self.segment_attributes.is_eflr = self.is_eflr

        self._bytes = None

    @abstractmethod
    def make_body_bytes(self) -> bytes:
        pass

    def _make_segment_attributes(self) -> bytes:
        """Writes the logical record segment attributes.

        .._RP66 V1 Logical Record Segment Header:
            http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1

        """

        return write_struct(RepresentationCode.USHORT, self.segment_attributes.reduce())

    @cached_property
    def size(self) -> int:
        """Calculates the size of the Logical Record Segment"""

        return self.represent_as_bytes().size

    def represent_as_bytes(self) -> np.ndarray:
        """Writes bytes of the entire Logical Record Segment that is an EFLR object"""

        if self._bytes is None:
            bts = self.make_body_bytes()
            bts = self.make_header_bytes(bts) + bts
            if self.segment_attributes.has_padding:
                bts += write_struct(RepresentationCode.USHORT, 1)

            self._bytes = np.frombuffer(bts, dtype=np.uint8)

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
    def split(self, is_first: bool, segment_length: int) -> bytes:
        """Creates header bytes to be inserted into split position

        When a Logical Record Segment overflows a Visible Record, it must be split.
        A split operation involves:
            1. Changing the header of the first part of the split
            2. Adding a header to the second part of the split

        Args:
            is_first: Represents whether this is the first or the last part of the split
            segment_length: Length of the segment after split operation

        Returns:
            Header bytes to be inserted into split position

        """

        assert segment_length % 2 == 0, 'Split segment length is not an EVEN NUMBER'
        assert segment_length < self.size, 'Split segment length can not be larger than the whole segment'

        _length = write_struct(RepresentationCode.UNORM, segment_length)

        toggle_padding = False

        if is_first:
            self.segment_attributes.has_predecessor_segment = False
            self.segment_attributes.has_successor_segment = True
            if self.segment_attributes.has_padding:
                toggle_padding = True
                self.segment_attributes.toggle_padding()

        else:
            self.segment_attributes.has_predecessor_segment = True
            self.segment_attributes.has_successor_segment = False

        _attributes = self._make_segment_attributes()

        if toggle_padding:
            self.segment_attributes.toggle_padding()

        return _length + _attributes + self.lr_type_struct

    def __repr__(self):
        """String representation of this object"""
        return self.set_type

    @classmethod
    @abstractmethod
    def make_lr_type_struct(cls, lr_type):
        pass

