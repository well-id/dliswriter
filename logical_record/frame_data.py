import math
import pandas as pd
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

    def __hash__(self):
        return hash(type(self)) + hash(self.frame_number)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self._frame_number == other.frame_number

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
    def __init__(self, frame: Frame, data: pd.DataFrame):
        self.flatten_dataframe(data)

        self._frame = frame
        self._data = data

        self.origin_reference = None

        self._i = 0

    @property
    def data(self):
        return self._data

    @property
    def frame(self):
        return self._frame

    def _make_frame_data(self, idx: int):
        return FrameData(
                frame=self._frame,
                frame_number=idx + 1,
                slots=self._data.iloc[idx],
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
    def flatten_dataframe(data: pd.DataFrame):
        for c in data.columns:
            c0 = data[c][0]
            if isinstance(c0, (list, np.ndarray)):
                new_names = [c + str(i + 1) for i in range(len(c0))]
                data[new_names] = pd.DataFrame(data[c].to_list(), index=data.index)
                data.drop(columns=[c], inplace=True)


