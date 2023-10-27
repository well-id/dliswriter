import numpy as np
from typing import List

from dlis_writer.logical_record.eflr_types import Frame, Channel
from dlis_writer.logical_record.iflr_types import FrameData
from dlis_writer.logical_record.collections.multi_logical_record import MultiLogicalRecord
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.converters import ReprCodeConverter


class MultiFrameData(MultiLogicalRecord):
    def __init__(self, frame: Frame, data: np.ndarray):
        super().__init__()

        self._data_array: np.ndarray = self.transform_structured_array(data, channels=frame.channels.value)
        self._frame = frame

        self._origin_reference = None

        self._i = 0

    def set_origin_reference(self, value):
        self._origin_reference = value

    def _make_frame_data(self, idx: int):
        return FrameData(
            frame=self._frame,
            frame_number=idx + 1,
            slots=self._data_array[idx],
            origin_reference=self._origin_reference
        )

    def __len__(self):
        return self._data_array.shape[0]

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
    def get_dtype(repr_code: RepresentationCode):
        if repr_code is None:
            return MultiFrameData.get_dtype(RepresentationCode.FDOUBL)

        return ReprCodeConverter.repr_codes_to_numpy_dtypes.get(repr_code)

    @staticmethod
    def transform_structured_array(data: np.ndarray, channels: List[Channel]):
        dtype_names = data.dtype.names

        if dtype_names is None:
            return data

        dtype = []
        for ch in channels:
            dt = (ch.name, MultiFrameData.get_dtype(ch.representation_code.value))
            if ch.dimension.value[0] > 1:
                dt = (*dt, tuple(ch.dimension.value))
            dtype.append(dt)
        arr = np.zeros(data.shape[0], dtype=dtype)
        for ch in channels:
            arr[ch.name] = data[ch.dataset_name]

        return arr
