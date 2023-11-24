import logging

from dlis_writer.logical_record.core.segment_attributes import SegmentAttributes
from dlis_writer.utils.enums import RepresentationCode as RepC
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
    padding = write_struct(RepC.USHORT, 1)

    def __init__(self, bts, lr_type_struct, is_eflr=False):
        super().__init__(bts)

        self.lr_type_struct = lr_type_struct
        self.is_eflr = is_eflr

    def make_segment(self, start_pos=0, n_bytes=None):
        if n_bytes is None:
            n_bytes = self._size - start_pos
            end_pos = None
            is_last = True
        else:
            end_pos = start_pos + n_bytes
            if end_pos > self._size:
                raise ValueError("Logical record too short for the requested bytes")
            is_last = end_pos == self._size

        if n_bytes < 12:
            raise ValueError(f"Logical Record segment body cannot be shorter than 12 bytes (got {n_bytes})")

        segment_attributes = SegmentAttributes(
            is_eflr=self.is_eflr,
            is_first=(start_pos == 0),
            is_last=is_last
        )

        size = n_bytes + 4
        if size % 2:
            size += 1
            segment_attributes.has_padding = True

        header_bytes = write_struct(RepC.UNORM, size) + segment_attributes.to_struct() + self.lr_type_struct

        new_bts = header_bytes + self._bts[start_pos:end_pos]
        if segment_attributes.has_padding:
            new_bts += self.padding

        return new_bts

    def make_segments(self, max_n_bytes):

        start_pos = 0
        remaining_size = self._size

        while remaining_size > 0:
            n_bytes = min(remaining_size, max_n_bytes)
            future_remaining_size = remaining_size - n_bytes
            if 0 < future_remaining_size < 12:
                n_bytes -= (12 - future_remaining_size)
                future_remaining_size = 12

            yield self.make_segment(start_pos, n_bytes), n_bytes + 4 + (n_bytes % 2)

            remaining_size = future_remaining_size
            start_pos += n_bytes


