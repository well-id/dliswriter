from dlis_writer.utils.converters import get_ascii_bytes
from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.eflr import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class FileHeader(EFLR):
    """Represents FILE-HEADER logical record type in RP66V1"""

    set_type = 'FILE-HEADER'
    identifier_length_limit = 65
    logical_record_type = LogicalRecordType.FHLR

    def __init__(self, identifier: str, sequence_number: int = 1, set_name=None):
        super().__init__(name='0', set_name=set_name)

        self.sequence_number = int(sequence_number)
        self.identifier = identifier

        if not isinstance(identifier, str):
            raise TypeError(f"'identifier' should be a str; got {type(identifier)}")
        if len(identifier) > self.identifier_length_limit:
            raise ValueError(f"'identifier' length should not exceed {self.identifier_length_limit} characters")

    def make_body_bytes(self) -> bytes:
        # BODY
        _body_bytes = b''
        _body_bytes += write_struct(RepresentationCode.USHORT, int('11110000', 2))
        _body_bytes += write_struct(RepresentationCode.IDENT, self.set_type)
        
        # TEMPLATE
        _body_bytes += write_struct(RepresentationCode.USHORT, int('00110100', 2))
        _body_bytes += write_struct(RepresentationCode.ASCII, 'SEQUENCE-NUMBER')
        _body_bytes += write_struct(RepresentationCode.USHORT, 20)
        
        _body_bytes += write_struct(RepresentationCode.USHORT, int('00110100', 2))
        _body_bytes += write_struct(RepresentationCode.ASCII, 'ID')
        _body_bytes += write_struct(RepresentationCode.USHORT, 20)

        # OBJECT
        _body_bytes += write_struct(RepresentationCode.USHORT, int('01110000', 2))
        _body_bytes += write_struct(RepresentationCode.OBNAME, self)

        # ATTRIBUTES
        _body_bytes += write_struct(RepresentationCode.USHORT, int('00100001', 2))
        _body_bytes += write_struct(RepresentationCode.USHORT, 10)
        _body_bytes += get_ascii_bytes(self.sequence_number, 10, justify_left=False)
        _body_bytes += write_struct(RepresentationCode.USHORT, int('00100001', 2))
        _body_bytes += write_struct(RepresentationCode.USHORT, 65)
        _body_bytes += get_ascii_bytes(self.identifier, 65, justify_left=True)

        return _body_bytes

