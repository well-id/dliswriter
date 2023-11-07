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
        
    def _make_template_bytes(self) -> bytes:
        bts = b''

        bts += write_struct(RepresentationCode.USHORT, int('00110100', 2))
        bts += write_struct(RepresentationCode.ASCII, 'SEQUENCE-NUMBER')
        bts += write_struct(RepresentationCode.USHORT, 20)

        bts += write_struct(RepresentationCode.USHORT, int('00110100', 2))
        bts += write_struct(RepresentationCode.ASCII, 'ID')
        bts += write_struct(RepresentationCode.USHORT, 20)

        return bts

    def _make_objects_bytes(self) -> bytes:
        bts = b''

        bts += write_struct(RepresentationCode.USHORT, int('00100001', 2))
        bts += write_struct(RepresentationCode.USHORT, 10)
        bts += get_ascii_bytes(self.sequence_number, 10, justify_left=False)
        bts += write_struct(RepresentationCode.USHORT, int('00100001', 2))
        bts += write_struct(RepresentationCode.USHORT, 65)
        bts += get_ascii_bytes(self.identifier, 65, justify_left=True)

        return bts

