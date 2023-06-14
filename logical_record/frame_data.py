import math
from functools import cached_property

from .utils.core import IFLR
from .utils.enums import Enum
from .utils.common import write_struct
from .utils.converters import get_representation_code
from .utils.enums import RepresentationCode


class FrameData(IFLR):

    def __init__(self,
                 frame=None,
                 frame_number:int=None,
                 slots=None):

        '''
    
        FrameData is an Implicitly Formatted Logical Record (IFLR)

        Each FrameData object begins with a reference to the Frame object
        that they belong to using OBNAME.

        :frame -> A Frame(EFLR) object instance
        :position -> Auto-assigned integer denoting the position of the FrameData
        
        :slots -> Represents a row in the dataframe. If there are 3 channels, slots will be the array
        of values at the corresponding index for those channels.

        '''

        super().__init__()

        self.frame = frame
        self.frame_number = frame_number # UVARI
        self.slots = slots # np.ndarray
        self.iflr_type = 0
        self.set_type = 'FDATA'


    @cached_property
    def body_bytes(self):

        _body = b''
        _body += self.frame.obname
        _body += write_struct(RepresentationCode.UVARI, self.frame_number)
        
        j = 0
        _channels = self.frame.channels.value
        for _channel in _channels:
            _representation_code = get_representation_code(_channel.representation_code.value,
                                                           from_value=True)
            _dimension = _channel.dimension.value

            for i in range(j, j+math.prod(_dimension)):
                _data = self.slots[i]
                _body += write_struct(_representation_code, _data)
                j += 1

        return _body


class NoFormatFrameData(IFLR):

    def __init__(self):

        super().__init__()
        self.iflr_type = 1

        self.no_format_object = None
        self.data = None

        self.set_type = 'NOFORMAT'

    @property
    def body_bytes(self):
        _body = b''
        _body += self.no_format_object.obname
        _body += self.data.encode('ascii')

        return _body