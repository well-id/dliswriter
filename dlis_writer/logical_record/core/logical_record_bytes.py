import logging

from dlis_writer.logical_record.core.segment_attributes import SegmentAttributes
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.common import write_struct


logger = logging.getLogger(__name__)


class BasicLogicalRecordBytes:
    def __init__(self, bts, key):

        self._bts = bts
        self._size = len(bts)
        self.key = key

    @property
    def bytes(self):
        return self._bts

    @property
    def size(self) -> int:
        return self._size


class LogicalRecordBytes(BasicLogicalRecordBytes):
    def __init__(self, bts, key, lr_type_struct, is_eflr=False):
        super().__init__(bts, key)

        self.lr_type_struct = lr_type_struct

        self.segment_attributes = SegmentAttributes()
        self.is_eflr = is_eflr
        if is_eflr:
            self.segment_attributes.is_eflr = True

        # self._add_header_bytes()

    def make_segment(self, start_pos=0, n_bytes=None):
        if n_bytes:
            if n_bytes < 12:
                raise ValueError(f"Logical Record segment body cannot be shorter than 12 bytes (got {n_bytes})")

            if n_bytes % 2:
                raise ValueError("Segment length must be an even number")

            end_pos = start_pos + n_bytes
            if end_pos > self._size:
                raise ValueError("Logical record too short for the requested bytes")
        else:
            if self._size - start_pos < 16:
                raise ValueError(f"Logical Record segment cannot be shorter than 16 bytes")
            end_pos = None

        lrs = LogicalRecordSegment(
            self._bts[start_pos:end_pos],
            lr_type_struct=self.lr_type_struct,
            is_eflr=self.is_eflr,
            is_first=(start_pos == 0),
            is_last=(end_pos == self._size)
        )

        return lrs.get_bytes()

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

        _attributes = self.segment_attributes.to_struct(no_padding=is_first)

        return write_struct(RepresentationCode.UNORM, segment_length) + _attributes + self.lr_type_struct

    # def _add_header_bytes(self):
    #     """Writes Logical Record Segment Header
    #
    #     .._RP66 V1 Logical Record Segment Header:
    #         http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1
    #
    #     """
    #
    #     segment_length = self.size + 4
    #     if segment_length % 2 != 0:
    #         segment_length += 1
    #         self.segment_attributes.has_padding = True
    #     else:
    #         self.segment_attributes.has_padding = False
    #
    #     header_bytes = write_struct(RepresentationCode.UNORM, segment_length) \
    #         + self.segment_attributes.to_struct()\
    #         + self.lr_type_struct
    #
    #     new_bts = header_bytes + self._bts
    #     if self.segment_attributes.has_padding:
    #         new_bts += write_struct(RepresentationCode.USHORT, 1)
    #
    #     self._bts = new_bts
    #     self._size = len(new_bts)


class LogicalRecordSegment:
    def __init__(self, bts, lr_type_struct, is_eflr=False, is_first=False, is_last=False):
        self._bts = bts
        self.lr_type_struct = lr_type_struct

        self.segment_attributes = SegmentAttributes()
        if is_eflr:
            self.segment_attributes.is_eflr = True
        self.segment_attributes.mark_order(first=is_first, last=is_last)

    def get_bytes(self) -> bytes:
        size = len(self._bts) + 4
        if size % 2 != 0:
            size += 1
            self.segment_attributes.has_padding = True
        else:
            self.segment_attributes.has_padding = False

        header_bytes = write_struct(RepresentationCode.UNORM, size) \
                       + self.segment_attributes.to_struct() \
                       + self.lr_type_struct

        new_bts = header_bytes + self._bts
        if self.segment_attributes.has_padding:
            new_bts += write_struct(RepresentationCode.USHORT, 1)

        return new_bts

