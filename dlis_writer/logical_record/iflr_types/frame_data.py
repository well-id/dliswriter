import math
from functools import lru_cache
from line_profiler_pycharm import profile

from dlis_writer.logical_record.core import IFLR
from dlis_writer.utils.common import write_struct
from dlis_writer.utils.converters import get_representation_code_from_value
from dlis_writer.utils.enums import RepresentationCode


class FrameData(IFLR):
    set_type = 'FDATA'

    def __init__(self, frame, frame_number: int, slots, origin_reference=None):

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

        self._frame = frame
        self._frame_number = frame_number  # UVARI
        self._slots = slots  # np.ndarray
        self.iflr_type = 0

        self.origin_reference = origin_reference

    @property
    def key(self):
        return hash(type(self)), self._frame_number

    @property
    def frame(self):
        return self._frame

    @property
    def frame_number(self) -> int:
        return self._frame_number

    @lru_cache()
    @profile
    def make_body_bytes(self) -> bytes:
        body = b''
        body += self.frame.obname
        body += write_struct(RepresentationCode.UVARI, self.frame_number)
        
        j = 0
        slots = self._slots
        for channel in self.frame.channels.value:
            representation_code = get_representation_code_from_value(channel.representation_code.value)

            for i in range(j, j+math.prod(channel.dimension.value)):
                body += write_struct(representation_code, slots[i])
                j += 1

        return body
