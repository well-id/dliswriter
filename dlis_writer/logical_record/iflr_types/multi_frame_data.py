import numpy as np
from line_profiler_pycharm import profile

from dlis_writer.logical_record.eflr_types.frame import Frame
from dlis_writer.logical_record.iflr_types.frame_data import FrameData


class MultiFrameData:
    def __init__(self, frame: Frame, data: np.ndarray, channel_name_mapping: dict = None):

        channels = [c.object_name for c in frame.channels.value]
        data = self.flatten_structured_array(data, channel_order=channels, channel_name_mapping=channel_name_mapping)

        self._data = data
        self._frame = frame

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
    def flatten_structured_array(data: np.ndarray, channel_order: list = None, channel_name_mapping: dict = None):
        dtype_names = data.dtype.names

        if dtype_names is None:
            return data

        if channel_order is not None:
            if channel_name_mapping is None:
                channel_name_mapping = {key: key for key in channel_order}

            if any(cn not in dtype_names for cn in channel_name_mapping.values()):
                raise ValueError(f"Channel names and data dtype names do not match: "
                                 f"\n{list(channel_name_mapping.values())}\nvs\n{dtype_names}")
            names = channel_order
        else:
            names = data.dtype.names
            channel_name_mapping = {key: key for key in names}

        return np.concatenate([np.atleast_2d(data[channel_name_mapping[key]].T) for key in names]).T
