import pytest
import numpy as np

from dlis_writer.logical_record.eflr_types.channel import Channel, ChannelObject
from dlis_writer.logical_record.eflr_types.axis import AxisObject
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.tests.common import base_data_path, config_params, make_config


@pytest.fixture
def chan():
    yield Channel.make_object("some_channel")


@pytest.fixture
def mock_data():
    dt = np.dtype([('time', float), ('amplitude', float, (10,)), ('radius', float, (12, 16))])
    return np.zeros(30, dtype=dt)


def test_from_config(config_params):
    channel: ChannelObject = Channel.make_object_from_config(config_params)

    conf = config_params['Channel']

    assert channel.name == conf['name']
    assert channel.name == conf['name']
    assert channel.dataset_name == conf["dataset_name"]

    assert channel.long_name.value == conf["long_name"]
    assert channel.properties.value == ["property1", "property 2 with multiple words"]
    assert channel.representation_code.value is RepresentationCode.FSINGL
    assert channel.units.value == 'acre'
    assert channel.dimension.value == [12]
    assert isinstance(channel.axis.value, list)
    assert isinstance(channel.axis.value[0], AxisObject)
    assert channel.axis.value[0].name == 'Axis-1'
    assert channel.element_limit.value == [12]
    assert channel.source.value == 'some source'
    assert channel.minimum_value.value == [0.]
    assert isinstance(channel.minimum_value.value[0], float)
    assert channel.maximum_value.value == [127.6]

    assert isinstance(channel.parent, Channel)


def test_from_config_alternative_name(config_params):
    channel: ChannelObject = Channel.make_object_from_config(config_params, key="Channel-1")

    assert channel.name == "Channel 1"
    assert channel.dataset_name == "Channel 1"  # not specified in config - same as channel name

    assert channel.dimension.value == [10, 10]
    assert channel.units.value == 'in'


@pytest.mark.parametrize(("prop_str", "prop_val"), (
        ("1, 2, 3", ["1", "2", "3"]),
        ("1word, 2 words, 3 w ords", ["1word", "2 words", "3 w ords"]),
        ("single_thing", ["single_thing"])
))
def test_properties(prop_str, prop_val):
    config = make_config("Channel488")
    config["Channel488"]["name"] = "ChanChan"
    config["Channel488"]["properties"] = prop_str

    channel: ChannelObject = Channel.make_object_from_config(config, key="Channel488")
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

    channel: ChannelObject = Channel.make_object_from_config(config)
    assert channel.dimension.value == channel.element_limit.value
    assert channel.dimension.value is not None
    assert channel.element_limit.value is not None


def test_dimension_and_element_limit_not_specified():
    config = make_config("Channel")
    config["Channel"]["name"] = "some channel"

    channel: ChannelObject = Channel.make_object_from_config(config)
    assert channel.dimension.value is None
    assert channel.element_limit.value is None


def test_dimension_and_element_limit_mismatch(caplog):
    config = make_config("Channel")
    config["Channel"]["name"] = "some channel"

    config["Channel"]["dimension"] = "12"
    config["Channel"]["element_limit"] = "12, 10"

    Channel.make_object_from_config(config)
    assert "For channel 'some channel', dimension is [12] and element limit is [12, 10]" in caplog.text


def test_multiple_channels_default_pattern(config_params):
    channels = Channel.make_all_objects_from_config(config_params)

    assert len(channels) == 9
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Channel 2"
    assert channels[2].name == "Channel 13"

    assert channels[0].dimension.value == [10, 10]
    assert channels[0].element_limit.value == [10, 10]
    assert channels[0].units.value == 'in'

    assert channels[1].dimension.value is None
    assert channels[1].element_limit.value is None
    assert channels[1].units.value is None

    assert channels[2].dimension.value == [128]
    assert channels[2].element_limit.value == [128]
    assert channels[2].units.value is None
    assert channels[2].dataset_name == "amplitude"


def test_multiple_channels_custom_pattern(config_params):
    channels = Channel.make_all_objects_from_config(config_params, key_pattern=r"Channel-\d")  # 1 digit only
    assert len(channels) == 2
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Channel 2"

    assert channels[0].dimension.value == [10, 10]
    assert channels[0].units.value == 'in'

    assert channels[1].dimension.value is None
    assert channels[1].units.value is None


def test_multiple_channels_list(config_params):
    channels = Channel.make_all_objects_from_config(config_params, keys=["Channel-1", "Channel"])

    assert len(channels) == 2
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Some Channel"

    assert channels[0].dimension.value == [10, 10]
    assert channels[0].units.value == 'in'

    assert channels[1].dimension.value == [12]
    assert channels[1].units.value == 'acre'


@pytest.mark.parametrize(("val", "unit"), (("s", 's'), ("T", 'T')))
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


@pytest.mark.parametrize(("value", "expected_value"), (
        (1, [1]),
        (10, [10]),
        ("10", [10]),
        ("10, ", [10]),
        ("10,    ", [10]),
        ("10, 11", [10, 11]),
        ("10, 11,  ", [10, 11]),
))
def test_setting_dimension(chan, value, expected_value):
    chan.dimension.value = value
    assert chan.dimension.value == expected_value


@pytest.mark.parametrize('value', ("", "10,, 10", 10.6, [10, 11.2]))
def test_setting_dimension_error(chan, value):
    with pytest.raises(ValueError):
        chan.dimension.value = value


@pytest.mark.parametrize(("value", "expected_value"), (
        ("p1, p2, p3", ["p1", "p2", "p3"]),
        ("p1, p2 with more words", ["p1", "p2 with more words"]),
        ("other. punctuation; signs", ["other. punctuation; signs"]),
        (["list, of, things"], ["list, of, things"])
))
def test_setting_properties(chan, value, expected_value):
    chan.properties.value = value
    assert chan.properties.value == expected_value


@pytest.mark.parametrize(("name", "dim"), (("time", [1]), ("amplitude", [10]), ('radius', [12, 16])))
def test_setting_dimension_from_data(chan, mock_data, name, dim):
    chan.name = name
    chan.set_dimension_and_repr_code_from_data(mock_data)
    assert chan.dimension.value == dim
    assert chan.element_limit.value == dim


@pytest.mark.parametrize(("name", "dim", "prev_dim"), (("time", [1], [30]), ("amplitude", [10], [1])))
def test_setting_dimension_from_data_mismatched_dimension(chan, mock_data, name, dim, prev_dim, caplog):
    chan.name = name
    chan.dimension.value = prev_dim
    chan.set_dimension_and_repr_code_from_data(mock_data)
    assert chan.dimension.value == dim
    assert "Previously defined dimension" in caplog.text


@pytest.mark.parametrize(("name", "dim", "prev_dim"), (("time", [1], [0]), ("radius", [12, 16], [12])))
def test_setting_dimension_from_data_mismatched_element_limit(chan, mock_data, name, dim, prev_dim, caplog):
    chan.name = name
    chan.element_limit.value = prev_dim
    chan.set_dimension_and_repr_code_from_data(mock_data)
    assert chan.element_limit.value == dim
    assert "Previously defined element limit" in caplog.text


@pytest.mark.parametrize("name", ("amp", "posix time"))
def test_setting_dimension_from_data_no_dataset_error(chan, mock_data, name):
    chan.name = name
    with pytest.raises(ValueError, match=f"no field of name {name}.*"):
        chan.set_dimension_and_repr_code_from_data(mock_data)


