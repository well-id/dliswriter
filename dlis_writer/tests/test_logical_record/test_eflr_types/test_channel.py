import pytest

from dlis_writer.logical_record.eflr_types import Channel
from dlis_writer.utils.enums import RepresentationCode, Units
from dlis_writer.tests.common import base_data_path, config_params, make_config


@pytest.fixture
def chan():
    yield Channel("some_channel")


def test_from_config(config_params):
    channel = Channel.from_config(config_params)

    conf = config_params['Channel']

    assert channel.object_name == conf['name']
    assert channel.name == conf['name']
    assert channel.dataset_name == conf["dataset_name"]

    assert channel.long_name.value == conf["long_name"]
    assert channel.properties.value == ["property1", "property 2 with multiple words"]
    assert channel.representation_code.value is RepresentationCode.FSINGL
    assert channel.units.value is Units.acre
    assert channel.dimension.value == [12]
    assert channel.axis.value == 'some axis'
    assert channel.element_limit.value == [12]
    assert channel.source.value == 'some source'
    assert channel.minimum_value.value == 0.
    assert isinstance(channel.minimum_value.value, float)
    assert channel.maximum_value.value == 127.6


def test_from_config_alternative_name(config_params):
    channel = Channel.from_config(config_params, key="Channel-1")

    assert channel.object_name == "Channel 1"
    assert channel.name == "Channel 1"
    assert channel.dataset_name == "Channel 1"  # not specified in config - same as channel name

    assert channel.dimension.value == [10, 10]
    assert channel.units.value == Units.in_


@pytest.mark.parametrize(("prop_str", "prop_val"), (
        ("1, 2, 3", ["1", "2", "3"]),
        ("1word, 2 words, 3 w ords", ["1word", "2 words", "3 w ords"]),
        ("single_thing", ["single_thing"])
))
def test_properties(prop_str, prop_val):
    config = make_config("Channel488")
    config["Channel488"]["name"] = "ChanChan"
    config["Channel488"]["properties"] = prop_str

    channel = Channel.from_config(config, key="Channel488")
    assert channel.name == "ChanChan"
    assert channel.properties.value == prop_val


@pytest.mark.parametrize(('dimension', 'element_limit'), (("10", None), ("10, 10", None), (None, "1, 2, 3")))
def test_dimension_and_element_limit(dimension, element_limit):
    config = make_config("Channel")
    config["Channel"]["name"] = "some channel"

    if dimension is not None:
        config["Channel"]["dimension"] = dimension

    if element_limit is not None:
        config["Channel"]["element_limit"] = element_limit

    channel = Channel.from_config(config)
    assert channel.dimension.value == channel.element_limit.value
    assert channel.dimension.value is not None
    assert channel.element_limit.value is not None


def test_dimension_and_element_limit_not_specified():
    config = make_config("Channel")
    config["Channel"]["name"] = "some channel"

    channel = Channel.from_config(config)
    assert channel.dimension.value == [1]
    assert channel.element_limit.value == [1]


def test_dimension_and_element_limit_mismatch(caplog):
    config = make_config("Channel")
    config["Channel"]["name"] = "some channel"

    config["Channel"]["dimension"] = "12"
    config["Channel"]["element_limit"] = "12, 10"

    Channel.from_config(config)
    assert "For channel 'some channel', dimension is [12] and element limit is [12, 10]" in caplog.text


def test_multiple_channels_default_pattern(config_params):
    channels = Channel.all_from_config(config_params)

    assert len(channels) == 8
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Channel 2"
    assert channels[2].name == "Channel 13"

    assert channels[0].dimension.value == [10, 10]
    assert channels[0].element_limit.value == [10, 10]
    assert channels[0].units.value == Units.in_

    assert channels[1].dimension.value == [1]
    assert channels[1].element_limit.value == [1]
    assert channels[1].units.value is None

    assert channels[2].dimension.value == [128]
    assert channels[2].element_limit.value == [128]
    assert channels[2].units.value is None
    assert channels[2].dataset_name == "amplitude"


def test_multiple_channels_custom_pattern(config_params):
    channels = Channel.all_from_config(config_params, key_pattern=r"Channel-\d")  # 1 digit only
    assert len(channels) == 2
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Channel 2"

    assert channels[0].dimension.value == [10, 10]
    assert channels[0].units.value == Units.in_

    assert channels[1].dimension.value == [1]
    assert channels[1].units.value is None


def test_multiple_channels_list(config_params):
    channels = Channel.all_from_config(config_params, keys=["Channel-1", "Channel"])

    assert len(channels) == 2
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Some Channel"

    assert channels[0].dimension.value == [10, 10]
    assert channels[0].units.value == Units.in_

    assert channels[1].dimension.value == [12]
    assert channels[1].units.value is Units.acre


@pytest.mark.parametrize(("val", "unit"), (("s", Units.s), ("second", Units.s), ("tesla", Units.T), ("T", Units.T)))
def test_setting_unit(chan, val, unit):
    chan.units.value = val
    assert chan.units.value is unit


def test_clearing_unit(chan):
    chan.units.value = None
    assert chan.units.value is None


@pytest.mark.parametrize(("val", "repr_code"), (
        (7, RepresentationCode.FDOUBL),
        ("FDOUBL", RepresentationCode.FDOUBL),
        ("USHORT", RepresentationCode.USHORT),
        ('15', RepresentationCode.USHORT)
))
def test_setting_repr_code(chan, val, repr_code):
    chan.representation_code.value = val
    assert chan.representation_code.value is repr_code


def test_clearing_repr_code(chan):
    chan.representation_code.value = None
    assert chan.representation_code.value is None


def test_attribute_set_directly_error(chan):
    with pytest.raises(RuntimeError, match="Cannot set DLIS Attribute 'units'.*"):
        chan.units = 'm'

    with pytest.raises(RuntimeError, match="Cannot set DLIS Attribute 'long_name'.*"):
        chan.long_name = 'Lorem ipsum'
