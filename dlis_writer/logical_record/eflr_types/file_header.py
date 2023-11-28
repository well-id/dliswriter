from dlis_writer.utils.converters import get_ascii_bytes
from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType


class FileHeaderObject(EFLRObject):
    """Model an object being part of FileHeader EFLR."""

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

        bts += write_struct(RepresentationCode.USHORT, int('00100001', 2))
        bts += write_struct(RepresentationCode.USHORT, 10)
        bts += get_ascii_bytes(self.sequence_number, 10, justify_left=False)
        bts += write_struct(RepresentationCode.USHORT, int('00100001', 2))
        bts += write_struct(RepresentationCode.USHORT, 65)
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

        bts += write_struct(RepresentationCode.USHORT, int('00110100', 2))
        bts += write_struct(RepresentationCode.ASCII, 'SEQUENCE-NUMBER')
        bts += write_struct(RepresentationCode.USHORT, 20)

        bts += write_struct(RepresentationCode.USHORT, int('00110100', 2))
        bts += write_struct(RepresentationCode.ASCII, 'ID')
        bts += write_struct(RepresentationCode.USHORT, 20)

        return bts

