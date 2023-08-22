from abc import abstractmethod
from ..common import write_struct
from ..enums import RepresentationCode


class IflrAndEflrBase:
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

    @abstractmethod
    def represent_as_bytes(self) -> bytes:
        pass

    @property
    @abstractmethod
    def header_bytes(self) -> bytes:
        pass

    @abstractmethod
    def split(self, is_first: bool, is_last: bool, segment_length: int, add_extra_padding: bool) -> bytes:
        pass

    def __repr__(self):
        """String representation of this object"""
        return self.set_type
