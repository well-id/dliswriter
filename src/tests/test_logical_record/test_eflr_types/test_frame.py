import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.frame import FrameTable, FrameItem
from dlis_writer.utils.enums import RepresentationCode

from tests.common import base_data_path, config_params


def test_from_config(config_params: ConfigParser):
    """Test creating d FrameObject from config."""

    frame: FrameItem = FrameTable.make_eflr_item_from_config(config_params)

    conf = config_params['Frame']
    assert frame.name == conf['name']

    assert frame.index_type.value == conf["index_type"]
    assert frame.encrypted.value == 1
    assert frame.description.value == conf["description.value"]

    assert frame.spacing.value == float(conf["spacing.value"])
    assert frame.spacing.units == 's'
    assert frame.spacing.representation_code is RepresentationCode.FDOUBL


@pytest.mark.parametrize(("channels_key", "channel_entry", "channel_names"), (
        ("channels", "Channel-rpm, Channel-amplitude", ("surface rpm", "amplitude")),
        ("channels.value", "Channel, Channel-1, Channel-thirteen", ("Some Channel", "Channel 1", "Channel 13"))
))
def test_from_config_with_channels(channels_key: str, channel_entry: str, channel_names: list[str],
                                   config_params: ConfigParser):
    """Test creating a FrameObject with specified channels from the config."""

    config_params["Frame"]["name"] = "Some frame"
    config_params["Frame"][channels_key] = channel_entry

    frame: FrameItem = FrameTable.make_eflr_item_from_config(config_params)

    assert frame.channels.value is not None
    assert len(frame.channels.value) == len(channel_names)

    for i, cn in enumerate(channel_names):
        assert frame.channels.value[i].name == cn
