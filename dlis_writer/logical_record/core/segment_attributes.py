from functools import lru_cache

from dlis_writer.utils.enums import RepresentationCode


class SegmentAttributes:
    weights = [2 ** i for i in range(8)][::-1]

    def __init__(self, is_eflr=False, is_first=False, is_last=False):
        self._value = [
            is_eflr,
            not is_first,
            not is_last,
            False,
            False,
            False,
            False,
            False
        ]

    @property
    def is_eflr(self) -> bool:
        return self._value[0]

    @is_eflr.setter
    def is_eflr(self, b: bool):
        self._value[0] = b

    @property
    def has_predecessor_segment(self) -> bool:
        return self._value[1]

    @has_predecessor_segment.setter
    def has_predecessor_segment(self, b: bool):
        self._value[1] = b

    @property
    def has_successor_segment(self) -> bool:
        return self._value[2]

    @has_successor_segment.setter
    def has_successor_segment(self, b: bool):
        self._value[2] = b

    @property
    def is_encrypted(self) -> bool:
        return self._value[3]

    @is_encrypted.setter
    def is_encrypted(self, b: bool):
        self._value[3] = b

    @property
    def has_encryption_protocol(self) -> bool:
        return self._value[4]

    @has_encryption_protocol.setter
    def has_encryption_protocol(self, b: bool):
        self._value[4] = b

    @property
    def has_checksum(self) -> bool:
        return self._value[5]

    @has_checksum.setter
    def has_checksum(self, b: bool):
        self._value[5] = b

    @property
    def has_trailing_length(self) -> bool:
        return self._value[6]

    @has_trailing_length.setter
    def has_trailing_length(self, b: bool):
        self._value[6] = b

    @property
    def has_padding(self) -> bool:
        return self._value[7]

    @has_padding.setter
    def has_padding(self, b: bool):
        self._value[7] = b

    def to_struct(self):
        return ushort(sum(map(lambda x, y: x * y, self._value, self.weights)))


@lru_cache
def ushort(v):
    return RepresentationCode.USHORT.converter.pack(v)
