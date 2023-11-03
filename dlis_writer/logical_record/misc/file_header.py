from dlis_writer.utils.converters import get_ascii_bytes
from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.logical_record import LogicalRecord
from dlis_writer.logical_record.core.logical_record_bytes import LogicalRecordBytes



class FileHeader(LogicalRecord):
    """Represents FILE-HEADER logical record type in RP66V1"""

    set_type = 'FILE-HEADER'
    identifier_length_limit = 65

    def __init__(self, identifier: str, sequence_number: int = 1):
        super().__init__()

        self.sequence_number = int(sequence_number)
        self.identifier = identifier

        if not isinstance(identifier, str):
            raise TypeError(f"'identifier' should be a str; got {type(identifier)}")
        if len(identifier) > self.identifier_length_limit:
            raise ValueError(f"'identifier' length should not exceed {self.identifier_length_limit} characters")
        
        self.origin_reference = None
        self.copy_number = 0
        self.name = '0'

    def represent_as_bytes(self) -> LogicalRecordBytes:
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

        lrb = self._make_lrb(_body_bytes)
        return lrb

    def _make_lrb(self, bts, **kwargs):
        return super()._make_lrb(bts, lr_type_struct=write_struct(RepresentationCode.USHORT, 0), is_eflr=True)
