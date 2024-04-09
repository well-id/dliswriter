import logging
import re
import pytest
import numpy as np

from dlis_writer.logical_record.eflr_types.frame import FrameSet, FrameItem
from dlis_writer.utils.internal_enums import RepresentationCode
from dlis_writer import DLISFile, high_compatibility_mode_decorator, enums


def test_frame_creation() -> None:
    """Test creating d FrameObject."""

    frame = FrameItem(
        "MAIN-FRAME",
        **{
            'index_type': 'BOREHOLE-DEPTH',
            'encrypted': 1,
            'description': "The main frame",
            'spacing': {'value': 0.2, 'units': 'm'}
        },
        parent=FrameSet()
    )

    assert frame.name == 'MAIN-FRAME'
    assert frame.index_type.value == 'BOREHOLE-DEPTH'
    assert frame.encrypted.value == 1
    assert frame.description.value == 'The main frame'

    assert frame.spacing.value == 0.2
    assert frame.spacing.units == 'm'
    assert frame.spacing.representation_code is RepresentationCode.FDOUBL

    assert isinstance(frame.parent, FrameSet)
    assert frame.parent.set_name is None


@pytest.mark.parametrize("channel_names", (
        ("Channel 1", "Channel 3", "Channel 2"),
        ("some_channel",)
))
def test_creation_with_channels(channel_names: tuple[str], channels: dict) -> None:
    """Test creating a FrameObject with specified channels."""

    frame = FrameItem(
        'Some frame',
        channels=[channels[k] for k in channel_names],
        parent=FrameSet()
    )

    assert frame.channels.value is not None
    assert len(frame.channels.value) == len(channel_names)

    for i, cn in enumerate(channel_names):
        assert frame.channels.value[i].name == cn


def _prepare_file_uneven_spacing() -> DLISFile:
    df = DLISFile()
    ch1 = df.add_channel("INDEX", data=np.arange(10) + np.random.rand(10))
    ch2 = df.add_channel("X", units="m", data=np.random.rand(10, 10))
    df.add_frame("MAIN", channels=(ch1, ch2), index_type=enums.FrameIndexType.NON_STANDARD)
    return df


def test_spacing_not_even(caplog: pytest.LogCaptureFixture):
    df = _prepare_file_uneven_spacing()

    with caplog.at_level(logging.WARNING, logger='dlis_writer'):
        df.generate_logical_records(chunk_size=None)
        assert "Spacing of the index channel" in caplog.text


@high_compatibility_mode_decorator
def test_spacing_not_even_high_compat_mode():
    df = _prepare_file_uneven_spacing()

    with pytest.raises(RuntimeError, match="Spacing of the index channel .* is not uniform.*"):
        df.generate_logical_records(chunk_size=None)

