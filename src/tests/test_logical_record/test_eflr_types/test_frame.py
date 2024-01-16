import pytest

from dlis_writer.logical_record.eflr_types.frame import FrameSet, FrameItem
from dlis_writer.utils.enums import RepresentationCode


def test_frame_creation() -> None:
    """Test creating d FrameObject."""

    frame = FrameItem(
        "MAIN-FRAME",
        **{
            'index_type': 'BOREHOLE-DEPTH',
            'encrypted': 1,
            'description': "The main frame",
            'spacing': {'value': 0.2, 'units': 'm', 'representation_code': 7}

        }
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
        channels=[channels[k] for k in channel_names]
    )

    assert frame.channels.value is not None
    assert len(frame.channels.value) == len(channel_names)

    for i, cn in enumerate(channel_names):
        assert frame.channels.value[i].name == cn
