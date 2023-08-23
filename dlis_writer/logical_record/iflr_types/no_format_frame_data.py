from dlis_writer.logical_record.core import IFLR


class NoFormatFrameData(IFLR):
    set_type = 'NOFORMAT'

    def __init__(self):

        super().__init__()
        self.iflr_type = 1

        self.no_format_object = None
        self.data = None

    @property
    def body_bytes(self):
        _body = b''
        _body += self.no_format_object.obname
        _body += self.data.encode('ascii')

        return _body
