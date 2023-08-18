from line_profiler_pycharm import profile

from .utils.converters import get_ascii_bytes
from .utils.common import write_struct
from .utils.enums import RepresentationCode


class FileHeader(object):
    """Represents FILE-HEADER logical record type in RP66V1"""

    def __init__(self,
                 sequence_number:int=1,
                 _id:str='DEFAULT FHLR'):

        self.sequence_number = sequence_number
        self._id = _id
        
        self.origin_reference = None
        self.copy_number = 0
        self.object_name = '0'

        self.set_type = 'FILE-HEADER'

    @profile
    def represent_as_bytes(self):
        # HEADER
        _length = write_struct(RepresentationCode.UNORM, 124)
        _attributes = write_struct(RepresentationCode.USHORT, int('10000000', 2))
        _type = write_struct(RepresentationCode.USHORT, 0)

        _header_bytes = _length + _attributes + _type

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
        _body_bytes += write_struct(RepresentationCode.OBNAME, (self.origin_reference,
                                               self.copy_number,
                                               self.object_name))

        # ATTRIBUTES
        _body_bytes += write_struct(RepresentationCode.USHORT, int('00100001', 2))
        _body_bytes += write_struct(RepresentationCode.USHORT, 10)
        _body_bytes += get_ascii_bytes(self.sequence_number, 10, justify_left=False)
        _body_bytes += write_struct(RepresentationCode.USHORT, int('00100001', 2))
        _body_bytes += write_struct(RepresentationCode.USHORT, 65)
        _body_bytes += get_ascii_bytes(self._id, 65, justify_left=True)

        _bytes = _header_bytes + _body_bytes
        
        return _bytes


    @property
    def size(self):
        return 124

    def __repr__(self):
        return self.set_type
