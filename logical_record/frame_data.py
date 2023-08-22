import math
import numpy as np
from line_profiler_pycharm import profile

from .utils.core import IFLR
from .utils.common import write_struct
from .utils.converters import get_representation_code_from_value
from .utils.enums import RepresentationCode
from logical_record.frame import Frame


class FrameData(IFLR):

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
        self.set_type = 'FDATA'

        self._body_bytes = None

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

    @property
    def body_bytes(self):
        if self._body_bytes is None:
            self._body_bytes = self._compute_body_bytes()
        return self._body_bytes

    @profile
    def _compute_body_bytes(self):
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


class MultiFrameData:
    def __init__(self, frame: Frame, data: np.ndarray):

        self._frame = frame
        self._data = self.flatten_structured_array(data)

        self.origin_reference = None

        self._i = 0

    @property
    def data(self):
        return self._data

    @property
    def frame(self):
        return self._frame

    @profile
    def _make_frame_data(self, idx: int):
        return FrameData(
                frame=self._frame,
                frame_number=idx + 1,
                slots=self._data[idx],
                origin_reference=self.origin_reference
        )

    def __len__(self):
        return self._data.shape[0]

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= len(self):
            raise StopIteration

        self._i += 1

        return self._make_frame_data(self._i - 1)

    def __getitem__(self, item: int):
        return self._make_frame_data(item)

    @staticmethod
    def flatten_structured_array(data: np.ndarray, channel_names: list = None):
        dtype_names = data.dtype.names

        if dtype_names is None:
            return data

        if channel_names is not None:
            if any(cn not in dtype_names for cn in channel_names):
                raise ValueError(f"Channel names and data dtype names do not match: "
                                 f"\n{channel_names}\nvs\n{dtype_names}")
            names = channel_names
        else:
            names = data.dtype.names

        return np.concatenate([np.atleast_2d(data[key].T) for key in names]).T
