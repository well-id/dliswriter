from functools import lru_cache

from dlis_writer.utils.enums import RepresentationCode


class SegmentAttributes:
    """Model metadata put in the header of each logical record segment."""

    weights = [2 ** i for i in range(8)][::-1]  # weights used to sum up the flags to represent as bytes later

    def __init__(self, is_eflr: bool = False, is_first: bool = False, is_last: bool = False):
        """Initialise SegmentAttributes.

        Args:
            is_eflr     :   True if the described logical record is an explicitly formatted one (EFLR); false otherwise.
            is_first    :   True if this is the first segment created from this logical record (no predecessors).
            is_last     :   True if this is the last segment created from this logical record (no successors).
        """

        self._value = [
            is_eflr,        #: EFLR or IFLR
            not is_first,   #: has predecessors
            not is_last,    #: has successors
            False,          #: is encrypted
            False,          #: has encryption protocol
            False,          #: has checksum
            False,          #: has trailing length
            False           #: has padding
        ]

    @property
    def has_padding(self) -> bool:
        """True if the described segment has a padding byte added; false otherwise."""

        return self._value[7]

    @has_padding.setter
    def has_padding(self, b: bool) -> None:
        """Set whether the described segment has a padding byte added."""

        self._value[7] = b

    def to_struct(self) -> bytes:
        """Transform the segment attributes to a number (by weighting and summing up flags) and that to bytes."""

        return ushort(sum(map(lambda x, y: x * y, self._value, self.weights)))


@lru_cache
def ushort(v: int) -> bytes:
    """Transform a number to bytes using USHORT format. Cache the results for future calls."""

    return RepresentationCode.USHORT.convert(v)
