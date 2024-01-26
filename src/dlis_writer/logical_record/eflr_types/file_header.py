from typing import Any

from dlis_writer.utils.converters import get_ascii_bytes
from dlis_writer.utils.struct_writer import write_struct_ascii
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType


def pack_ushort(v: int) -> bytes:
    return RepresentationCode.USHORT.convert(v)


class FileHeaderItem(EFLRItem):
    """Model an object being part of FileHeader EFLR."""

    parent: "FileHeaderSet"

    header_id_length_limit = 65             #: max length of the file header name
    max_sequence_number = int(1e10 - 1)     #: max value for sequence number; largest 10-digit integer

    def __init__(self, header_id: str, parent: "FileHeaderSet", sequence_number: int = 1) -> None:
        """Initialise FileHeaderItem.

        Args:
            header_id       :   Name of the FileHeaderItem.
            parent          :   Parent FileHeaderSet of this FileHeaderItem.
            sequence_number :   Sequence number of the file. Must be a positive integer whose ASCII representation
                                does not exceed 10 characters.
        """

        if not isinstance(header_id, str):
            raise TypeError(f"'header_id' should be a str; got {type(header_id)}")
        if len(header_id) > self.header_id_length_limit:
            raise ValueError(f"'header_id' length should not exceed {self.header_id_length_limit} characters")

        if not isinstance(sequence_number, int):
            raise TypeError(f"Expected an integer; got {type(sequence_number)}: {sequence_number}")
        if not 0 < sequence_number <= self.max_sequence_number:
            raise ValueError(f"Sequence number must be a positive integer not larger than {self.max_sequence_number}; "
                             f"got {sequence_number}")

        self.header_id = header_id
        self.sequence_number = sequence_number

        super().__init__(name='0', parent=parent)

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(header_id={self.header_id}, sequence_number={self.sequence_number}, "
                f"parent=FileHeaderSet())")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False

        if not self.sequence_number == other.sequence_number:
            return False

        if not self.header_id == other.header_id:
            return False

        if not self.parent.set_name == other.parent.set_name:
            return False

        return True

    def _make_attrs_bytes(self) -> bytes:
        """Create bytes describing the values of attributes of FIleHeaderItem."""

        bts = b''

        bts += pack_ushort(int('00100001', 2))
        bts += pack_ushort(10)
        bts += get_ascii_bytes(str(self.sequence_number), 10, justify_left=False)
        bts += pack_ushort(int('00100001', 2))
        bts += pack_ushort(65)
        bts += get_ascii_bytes(self.header_id, 65, justify_left=True)

        return bts


class FileHeaderSet(EFLRSet):
    """Model FileHeader EFLR."""

    set_type = 'FILE-HEADER'
    logical_record_type = EFLRType.FHLR
    item_type = FileHeaderItem

    def __init__(self) -> None:
        super().__init__(set_name=None)

    def _make_template_bytes(self) -> bytes:
        """Create bytes describing the template - kinds of attributes to be found in the FileHeader EFLR."""

        bts = b''

        bts += pack_ushort(int('00110100', 2))
        bts += write_struct_ascii('SEQUENCE-NUMBER')
        bts += pack_ushort(20)

        bts += pack_ushort(int('00110100', 2))
        bts += write_struct_ascii('ID')
        bts += pack_ushort(20)

        return bts


FileHeaderItem.parent_eflr_class = FileHeaderSet
