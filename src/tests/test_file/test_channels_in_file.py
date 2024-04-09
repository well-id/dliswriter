import pytest
import logging
import numpy as np

from dlis_writer import DLISFile, high_compatibility_mode_decorator, enums


def _prepare_file_channel_not_in_frame() -> DLISFile:
    df = DLISFile()
    df.add_origin("ORIGIN")
    ch1 = df.add_channel("INDEX", data=np.arange(10))
    df.add_channel("X", units="m", data=np.random.rand(10, 10))  # not added to frame
    ch3 = df.add_channel("Y", data=np.arange(10, 20))
    df.add_frame("MAIN", channels=(ch1, ch3), index_type=enums.FrameIndexType.NON_STANDARD)

    return df


def test_channel_not_in_frame(caplog: pytest.LogCaptureFixture):

    with caplog.at_level(logging.WARNING, logger='dlis_writer'):
        df = _prepare_file_channel_not_in_frame()
        df.check_objects()
        assert "has not been added to any frame" in caplog.text


@high_compatibility_mode_decorator
def test_channel_not_in_frame_high_compat_mode():
    df = _prepare_file_channel_not_in_frame()

    with pytest.raises(RuntimeError, match="Channel.* has not been added to any frame.*"):
        df.check_objects()

