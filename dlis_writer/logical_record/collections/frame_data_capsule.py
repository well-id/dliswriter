import numpy as np
from itertools import chain
from typing import List

from dlis_writer.logical_record.eflr_types import Frame, Channel
from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.logical_record.collections.multi_logical_record import MultiLogicalRecord


class FrameDataCapsule(MultiLogicalRecord):
    def __init__(self, frame: Frame, data: np.ndarray):
        super().__init__()
        self._frame: Frame = frame
        self._data: MultiFrameData = MultiFrameData(frame, data)

    @property
    def frame(self) -> Frame:
        return self._frame

    @property
    def channels(self) -> List[Channel]:
        return self.frame.channels.value or []

    @property
    def data(self) -> MultiFrameData:
        return self._data

    @property
    def origin_reference(self):
        return self._data.origin_reference

    @origin_reference.setter
    def origin_reference(self, val):
        self._data.origin_reference = val

    def __len__(self):
        return len(self.channels) + 1 + len(self.data)

    def __iter__(self):
        return chain(self.channels, (self.frame,), self.data)


