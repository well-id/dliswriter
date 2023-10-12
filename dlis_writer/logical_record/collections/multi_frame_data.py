import numpy as np
from typing import List
from line_profiler_pycharm import profile

from dlis_writer.logical_record.eflr_types import Frame, Channel
from dlis_writer.logical_record.iflr_types import FrameData


class MultiFrameData:
    def __init__(self, frame: Frame, data: np.ndarray):

        self._data_array: np.ndarray = self.flatten_structured_array(data, channels=frame.channels.value)
        self._frame = frame

        self.origin_reference = None

        self._i = 0

    def _make_frame_data(self, idx: int):
        return FrameData(
            frame=self._frame,
            frame_number=idx + 1,
            slots=self._data_array[idx],
            origin_reference=self.origin_reference
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
    def flatten_structured_array(data: np.ndarray, channels: List[Channel] = None):
        dtype_names = data.dtype.names

        if dtype_names is None:
            return data

        if channels is not None:
            channel_name_mapping = {ch.name: ch.dataset_name for ch in channels}

            if any(cn not in dtype_names for cn in channel_name_mapping.values()):
                raise ValueError(f"Channel names and data dtype names do not match: "
                                 f"\n{list(channel_name_mapping.values())}\nvs\n{dtype_names}")
            names = list(channel_name_mapping.keys())
        else:
            names = data.dtype.names
            channel_name_mapping = {key: key for key in names}

        return np.concatenate([np.atleast_2d(data[channel_name_mapping[key]].T) for key in names]).T
