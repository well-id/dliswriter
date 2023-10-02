from dlis_writer.logical_record.core.iflr import IFLR, make_iflr_type_struct


class NoFormatFrameData(IFLR):
    set_type = 'NOFORMAT'
    iflr_type = 1
    iflr_type_struct = make_iflr_type_struct(iflr_type)

    def __init__(self):

        super().__init__()

        self.no_format_object = None
        self.data = None

    def make_body_bytes(self) -> bytes:
        _body = b''
        _body += self.no_format_object.obname
        _body += self.data.encode('ascii')

        return _body
