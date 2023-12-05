from dlis_writer.utils.converters import get_ascii_bytes
from dlis_writer.utils.struct_writer import write_struct_ascii
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType


def pack_ushort(v):
    return RepresentationCode.USHORT.converter.pack(v)


class FileHeaderObject(EFLRObject):
    """Model an object being part of FileHeader EFLR."""

    parent: "FileHeader"

    identifier_length_limit = 65    #: max length of the file header name

    def __init__(self, identifier: str, parent: "FileHeader", sequence_number: int = 1, **kwargs):
        """Initialise FileHeaderObject.

        Args:
            identifier      :   Name of the FileHeaderObject.
            parent          :   FileHeader EFLR instance this FileHeaderObject belongs to.
            sequence_number :   Sequence number of the file.
            **kwargs        :   Values of to be set as characteristics of the FileHeaderObject Attributes.
        """

        self.identifier = identifier
        self.sequence_number = int(sequence_number)

        if not isinstance(identifier, str):
            raise TypeError(f"'identifier' should be a str; got {type(identifier)}")
        if len(identifier) > self.identifier_length_limit:
            raise ValueError(f"'identifier' length should not exceed {self.identifier_length_limit} characters")

        super().__init__(name='0', parent=parent, **kwargs)

    def _make_attrs_bytes(self) -> bytes:
        """Create bytes describing the values of attributes of FIleHeaderObject."""

        bts = b''

        bts += pack_ushort(int('00100001', 2))
        bts += pack_ushort(10)
        bts += get_ascii_bytes(str(self.sequence_number), 10, justify_left=False)
        bts += pack_ushort(int('00100001', 2))
        bts += pack_ushort(65)
        bts += get_ascii_bytes(self.identifier, 65, justify_left=True)

        return bts


class FileHeader(EFLR):
    """Model FileHeader EFLR."""

    set_type = 'FILE-HEADER'
    logical_record_type = EFLRType.FHLR
    object_type = FileHeaderObject

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
