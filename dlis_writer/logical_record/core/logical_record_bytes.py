import logging

from dlis_writer.logical_record.core.segment_attributes import SegmentAttributes
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.common import write_struct


logger = logging.getLogger(__name__)


class BasicLogicalRecordBytes:
    def __init__(self, bts):

        self._bts = bts
        self._size = len(bts)

    @property
    def bytes(self):
        return self._bts

    @property
    def size(self) -> int:
        return self._size


class LogicalRecordBytes(BasicLogicalRecordBytes):
    def __init__(self, bts, lr_type_struct, is_eflr=False):
        super().__init__(bts)

        self.lr_type_struct = lr_type_struct

        self.segment_attributes = SegmentAttributes()
        self.is_eflr = is_eflr
        if is_eflr:
            self.segment_attributes.is_eflr = True

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
            if self._size - start_pos < 12:
                raise ValueError(f"Logical Record segment body cannot be shorter than 12 bytes")
            end_pos = None

        lrs = LogicalRecordSegment(
            self._bts[start_pos:end_pos],
            lr_type_struct=self.lr_type_struct,
            is_eflr=self.is_eflr,
            is_first=(start_pos == 0),
            is_last=(end_pos is None or end_pos == self._size)
        )

        return lrs.get_bytes()


class LogicalRecordSegment:
    def __init__(self, bts, lr_type_struct, **kwargs):
        self._bts = bts
        self.lr_type_struct = lr_type_struct

        self.segment_attributes = SegmentAttributes(**kwargs)

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

