from abc import abstractmethod
from functools import lru_cache
from line_profiler_pycharm import profile

from ..common import write_struct
from ..enums import RepresentationCode


class IFLR:
    """Similar to EFLR object with is_eflr=False

    Methods docstrings are not added as they are the same with EFLR.
    """

    def __init__(self):

        self.logical_record_type = None
        self.iflr_type = None

        self.is_eflr = False
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

        _bits = f'{int(self.is_eflr)}' \
                f'{int(self.has_predecessor_segment)}' \
                f'{int(self.has_successor_segment)}' \
                f'{int(self.is_encrypted)}' \
                f'{int(self.has_encryption_protocol)}' \
                f'{int(self.has_checksum)}' \
                f'{int(self.has_trailing_length)}' \
                f'{int(self.has_padding)}'

        return write_struct(RepresentationCode.USHORT, int(_bits, 2))

    @property
    def size(self):
        return len(self.represent_as_bytes())

    @property
    def header_bytes(self) -> bytes:
        self.segment_length = len(self.body_bytes) + 4
        if self.segment_length % 2 != 0:
            self.segment_length += 1
            self.has_padding = True
        else:
            self.has_padding = False

        return write_struct(RepresentationCode.UNORM, self.segment_length) \
            + self.segment_attributes \
            + write_struct(RepresentationCode.USHORT, self.iflr_type)

    @lru_cache()
    @profile
    def represent_as_bytes(self):
        _bytes = self.body_bytes  # Create
        _bytes = self.header_bytes + _bytes
        if self.has_padding:
            _bytes += write_struct(RepresentationCode.USHORT, 1)  # Padding

        return _bytes

    def split(self, is_first: bool, is_last: bool, segment_length: int, add_extra_padding: bool) -> bytes:
        """Returns header bytes to be inserted into split position(s)"""

        assert int(is_first) + int(is_last) != 2, 'Splitted segment can not be both FIRST and LAST'
        assert segment_length % 2 == 0, 'Splitted segment length is not an EVEN NUMBER'
        assert segment_length < self.size, 'Splitted segment length can not be larger than the whole segment'

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

        return _length + _attributes + write_struct(RepresentationCode.USHORT, self.iflr_type)

    def __repr__(self):
        return self.set_type
