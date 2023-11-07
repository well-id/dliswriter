from dlis_writer.logical_record.core.iflr import IFLR
from dlis_writer.utils.enums import IFLRType


class NoFormatFrameData(IFLR):
    logical_record_type = IFLRType.NOFMT

    def __init__(self):

        super().__init__()

        self.no_format_object = None
        self.data = None

    def make_body_bytes(self) -> bytes:
        _body = b''
        _body += self.no_format_object.obname
        _body += self.data.encode('ascii')

        return _body
