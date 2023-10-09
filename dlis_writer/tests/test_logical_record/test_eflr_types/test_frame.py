import pytest

from dlis_writer.logical_record.eflr_types import Frame
from dlis_writer.utils.enums import RepresentationCode, Units
from dlis_writer.tests.common import base_data_path, config_params, make_config_for_object


def test_from_config(config_params):
    frame = Frame.from_config(config_params)

    assert frame.object_name == config_params['Frame']['name']

    conf = config_params['Frame.attributes']
    assert frame.index_type.value == conf["index_type"]
    assert frame.encrypted.value is True
    assert frame.description.value == conf["description.value"]

    assert frame.spacing.value == float(conf["spacing.value"])
    assert frame.spacing.units is Units.s
    assert frame.spacing.representation_code is RepresentationCode.FDOUBL


@pytest.mark.parametrize("channels_key", ("channels", "channels.value"))
def test_from_config_with_channels(channels_key):
    config = make_config_for_object("Frame")
    config["Frame"]["name"] = "Some frame"
    config["Frame.attributes"][channels_key] = "sth"

    with pytest.raises(RuntimeError, match="Frame channels cannot be defined.*"):
        Frame.from_config(config)
