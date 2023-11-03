import numpy as np
import logging

from dlis_writer.logical_record.core.segment_attributes import SegmentAttributes
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.common import write_struct


logger = logging.getLogger(__name__)


class BasicLogicalRecordBytes:
    def __init__(self, bts, key):

        self._bts = np.frombuffer(bts, dtype=np.uint8)
        self.key = key

    @property
    def bytes(self):
        return self._bts

    @property
    def size(self) -> int:
        return self._bts.size


class LogicalRecordBytes(BasicLogicalRecordBytes):
    def __init__(self, bts, key, lr_type_struct, is_eflr=False):
        super().__init__(bts, key)

        self.lr_type_struct = lr_type_struct

        self.segment_attributes = SegmentAttributes()
        if is_eflr:
            self.segment_attributes.is_eflr = True

        self._add_header_bytes()

    @property
    def bytes(self):
        return self._bts

    @property
    def size(self) -> int:
        return self._bts.size

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

        if self.lr_type_struct is None:
            raise RuntimeError("LR type struct is undefined")

        self.segment_attributes.mark_order(first=is_first, last=is_last)

        _attributes = self.segment_attributes.to_struct(no_padding=is_first)

        return write_struct(RepresentationCode.UNORM, segment_length) + _attributes + self.lr_type_struct

    def _add_header_bytes(self):
        """Writes Logical Record Segment Header

        .._RP66 V1 Logical Record Segment Header:
            http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1

        """

        segment_length = self.size + 4
        if segment_length % 2 != 0:
            segment_length += 1
            self.segment_attributes.has_padding = True
        else:
            self.segment_attributes.has_padding = False

        header_bytes = write_struct(RepresentationCode.UNORM, segment_length) \
            + self.segment_attributes.to_struct()\
            + self.lr_type_struct

        new_bts = header_bytes + self._bts.tobytes()
        if self.segment_attributes.has_padding:
            new_bts += write_struct(RepresentationCode.USHORT, 1)

        self._bts = np.frombuffer(new_bts, dtype=np.uint8)

