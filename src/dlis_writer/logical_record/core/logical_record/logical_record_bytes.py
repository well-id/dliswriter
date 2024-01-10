import logging
from typing import Optional, Generator

from dlis_writer.logical_record.core.logical_record.segment_attributes import SegmentAttributes
from dlis_writer.utils.enums import RepresentationCode as RepC


logger = logging.getLogger(__name__)


class LogicalRecordBytes:
    """Wrap bytes of a LogicalRecord and StorageUnitLabel, adding segmenting functionalities."""

    padding: bytes = RepC.USHORT.convert(1)  #: padding byte added if the number of bytes in a segment is odd

    def __init__(self, bts: bytes, lr_type_struct: bytes, is_eflr: bool = False):
        """Initialise a LogicalRecordBytes object.

        Args:
            bts             :   Full bytes describing a logical record.
            lr_type_struct  :   Bytes describing the type of the logical record.
            is_eflr         :   True if the bytes describe an explicitly formatted logical record, False otherwise.
        """

        self._bts = bts
        self._size = len(bts)

        self._lr_type_struct = lr_type_struct
        self._is_eflr = is_eflr

    @property
    def bts(self) -> bytes:
        """Bytes describing a logical record."""

        return self._bts

    @property
    def size(self) -> int:
        """Number of bytes in the logical record description."""

        return self._size

    def make_segment(self, start_pos: int = 0, n_bytes: Optional[int] = None) -> tuple[bytes, int]:
        """Create a segment of the logical record bytes.

        Logical record bytes are often too long to fit into a visible record (physical unit of a DLIS file).
        In such case, they have to be split into several segments. Each segment should have a header which includes
        metadata such as segment size, whether this is the first/last segment of this logical record, what is the type
        of the logical record, etc.

        Args:
            start_pos   :   Starting index of the segment.
            n_bytes     :   Number of bytes - following the starting index - to be put in the segment. If not specified,
                            all bytes from start_pos will be included.

        Returns:
            2-tuple of:
                bytes   :   Bytes of the logical record segment, including the header with metadata.
                int     :   Total size of the segment (in bytes).
        """

        if n_bytes is None:  # include all bytes from start_pos till the end
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
            is_eflr=self._is_eflr,
            is_first=(start_pos == 0),
            is_last=is_last
        )

        size = n_bytes + 4  # adding header size - 4 bytes
        if size % 2:
            # total segment size must be even; if the number of bytes is odd, add a padding byte
            size += 1
            segment_attributes.has_padding = True

        header_bytes = RepC.UNORM.convert(size) + segment_attributes.to_struct() + self._lr_type_struct

        new_bts = header_bytes + self._bts[start_pos:end_pos]
        if segment_attributes.has_padding:
            new_bts += self.padding  # add the promised padding byte

        return new_bts, size

    def make_segments(self, max_n_bytes: int) -> Generator:
        """Define a generator which splits the logical record bytes into segments of given maximal size.

        See make_segment for a more detailed description.

        Args:
            max_n_bytes :   Maximal number of bytes in a segment body. Note that 4 more bytes will be added for the
                            header (and one more byte for the padding if the number of bytes is odd).
                            Must be an integer of minimal value of 12. Only this condition (>= 12) is checked;
                            other checks (type etc.) are left out for performance reasons.

        Yields:
            bytes   :   Bytes of a logical record segment, including an added header.
        """

        start_pos = 0  # start from the beginning of the logical record bytes
        remaining_size = self._size  # all bytes will be processed; self._size is assumed to always be >=12

        if max_n_bytes < 24:
            # minimal length of a logical record segment is 16 (of which 4 bytes are reserved for header),
            # so for the splitting to work correctly max_n_bytes must be >= 24, which is twice the min segment body size
            raise ValueError(f"Max size of a logical record segment body cannot be less than 24 (got {max_n_bytes})")

        while remaining_size > 0:
            n_bytes = min(remaining_size, max_n_bytes)  # size of the current (to be created) segment body
            future_remaining_size = remaining_size - n_bytes  # how many bytes will be left for a next segment
            if 0 < future_remaining_size < 12:
                # the next segment would be shorter than 12 bytes, and this is not allowed
                # so the current segment must be shortened by a few bytes which will be passed over to the next segment;
                n_bytes -= (12 - future_remaining_size)
                future_remaining_size = 12

            yield self.make_segment(start_pos, n_bytes)

            # update values before next iteration of the loop
            remaining_size = future_remaining_size
            start_pos += n_bytes
