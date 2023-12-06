import pytest
from _pytest.logging import LogCaptureFixture
import numpy as np
from configparser import ConfigParser
from typing import Union, Any

from dlis_writer.logical_record.eflr_types.channel import Channel, ChannelObject
from dlis_writer.logical_record.eflr_types.axis import AxisObject
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.source_data_objects import NumpyInterface

from tests.common import base_data_path, config_params, make_config


@pytest.fixture
def chan():
    """Mock ChannelObject instance for tests."""

    yield Channel.make_object("some_channel")


@pytest.fixture
def mock_data() -> NumpyInterface:
    """Mock data (structured numpy array) for tests."""

    dt = np.dtype([('time', float), ('amplitude', float, (10,)), ('radius', float, (12,))])
    return NumpyInterface(np.zeros(30, dtype=dt))


def test_from_config(config_params: ConfigParser):
    """Check that a ChannelObject is correctly set up from config info."""

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


def test_from_config_alternative_name(config_params: ConfigParser):
    """Check that a CalibrationObject is correctly set up from config info and explicitly specified section name."""

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
def test_properties(prop_str: str, prop_val: list[str]):
    """Check that channel properties are set up correctly from config."""

    config = make_config("Channel488")
    config["Channel488"]["name"] = "ChanChan"
    config["Channel488"]["properties"] = prop_str

    channel: ChannelObject = Channel.make_object_from_config(config, key="Channel488")
    assert channel.name == "ChanChan"
    assert channel.properties.value == prop_val


@pytest.mark.parametrize(('dimension', 'element_limit'), (("10", None), ("10, 10", None), (None, "1, 2, 3")))
def test_dimension_and_element_limit(dimension: Union[str, None], element_limit: Union[str, None]):
    """Test that it is enough to specify dimension OR element limit in the config for both to be set to that value."""

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
    """Test that if neither dimension nor element limit are specified, none of them is set."""

    config = make_config("Channel")
    config["Channel"]["name"] = "some channel"

    channel: ChannelObject = Channel.make_object_from_config(config)
    assert channel.dimension.value is None
    assert channel.element_limit.value is None


def test_dimension_and_element_limit_mismatch(caplog: LogCaptureFixture):
    """Test that if dimension and element limit do not match, this fact is included as a warning in log messages."""

    config = make_config("Channel")
    config["Channel"]["name"] = "some channel"

    config["Channel"]["dimension"] = "12"
    config["Channel"]["element_limit"] = "12, 10"

    Channel.make_object_from_config(config)
    assert "For channel 'some channel', dimension is [12] and element limit is [12, 10]" in caplog.text


def test_multiple_channels_default_pattern(config_params: ConfigParser):
    """Test creating all channels with config section names following the default pattern (r'Channel-\w+')."""

    channels: list[ChannelObject] = Channel.make_all_objects_from_config(config_params)

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


def test_multiple_channels_custom_pattern(config_params: ConfigParser):
    """Test creating channels whose config section names follow a custom regex pattern."""

    # pattern: 1 digit only
    channels: list[ChannelObject] = Channel.make_all_objects_from_config(config_params, key_pattern=r"Channel-\d")
    assert len(channels) == 2
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Channel 2"

    assert channels[0].dimension.value == [10, 10]
    assert channels[0].units.value == 'in'

    assert channels[1].dimension.value is None
    assert channels[1].units.value is None


def test_multiple_channels_list(config_params: ConfigParser):
    """Test creating channels by providing config section names in a list."""

    channels: list[ChannelObject] = Channel.make_all_objects_from_config(config_params, keys=["Channel-1", "Channel"])

    assert len(channels) == 2
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Some Channel"

    assert channels[0].dimension.value == [10, 10]
    assert channels[0].units.value == 'in'

    assert channels[1].dimension.value == [12]
    assert channels[1].units.value == 'acre'


@pytest.mark.parametrize(("val", "unit"), (("s", 's'), ("T", 'T')))
def test_setting_unit(chan: ChannelObject, val: str, unit: str):
    """Test setting Attribute 'units' of Channel."""

    chan.units.value = val
    assert chan.units.value is unit


def test_clearing_unit(chan: ChannelObject):
    """Test removing previously defined channel unit."""

    chan.units.value = None
    assert chan.units.value is None


@pytest.mark.parametrize(("val", "repc"), (
        (7, RepresentationCode.FDOUBL),
        ("FDOUBL", RepresentationCode.FDOUBL),
        ("USHORT", RepresentationCode.USHORT),
        ('15', RepresentationCode.USHORT),
        (RepresentationCode.UVARI, RepresentationCode.UVARI)
))
def test_setting_repr_code(chan: ChannelObject, val: Union[str, int, RepresentationCode], repc: RepresentationCode):
    """Test that representation code is correctly set, whether the name, value, or the enum member itself is passed."""

    chan.representation_code.value = val
    assert chan.representation_code.value is repc


def test_clearing_repr_code(chan: ChannelObject):
    """Test removing previously defined representation code."""

    chan.representation_code.value = None
    assert chan.representation_code.value is None


def test_attribute_set_directly_error(chan: ChannelObject):
    """Test that a RuntimeError is raised if an attempt to set an Attribute directly is made."""

    with pytest.raises(RuntimeError, match="Cannot set DLIS Attribute 'units'.*"):
        chan.units = 'm'    # type: ignore  # mypy property setter bug

    with pytest.raises(RuntimeError, match="Cannot set DLIS Attribute 'long_name'.*"):
        chan.long_name = 'Lorem ipsum'    # type: ignore  # mypy property setter bug


@pytest.mark.parametrize(("value", "expected_value"), (
        (1, [1]),
        (10, [10]),
        ("10", [10]),
        ("10, ", [10]),
        ("10,    ", [10]),
        ("10, 11", [10, 11]),
        ("10, 11,  ", [10, 11]),
))
def test_setting_dimension(chan: ChannelObject, value: Union[int, str], expected_value: list[int]):
    """Test that channel dimension is correctly parsed from str or int."""

    chan.dimension.value = value
    assert chan.dimension.value == expected_value


@pytest.mark.parametrize('value', ("", "10,, 10", 10.6, [10, 11.2]))
def test_setting_dimension_error(chan: ChannelObject, value: Any):
    """Test that a ValueError is raised if an un-parsable value is attempted to be set as dimension."""

    with pytest.raises(ValueError):
        chan.dimension.value = value


@pytest.mark.parametrize(("value", "expected_value"), (
        ("p1, p2, p3", ["p1", "p2", "p3"]),
        ("p1, p2 with more words", ["p1", "p2 with more words"]),
        ("other. punctuation; signs", ["other. punctuation; signs"]),
        (["list, of, things"], ["list, of, things"])
))
def test_setting_properties(chan: ChannelObject, value: Union[str, list[str]], expected_value: list[str]):
    """Test that 'properties' attribute of channel parses the input correctly (splitting str at commas)."""

    chan.properties.value = value
    assert chan.properties.value == expected_value


@pytest.mark.parametrize(("name", "dim"), (("time", [1]), ("amplitude", [10]), ('radius', [12])))
def test_setting_dimension_from_data(chan: ChannelObject, mock_data: NumpyInterface, name: str, dim: list[int]):
    """Check that dimension and element limit are correctly inferred from data."""

    chan.name = name
    chan.set_dimension_and_repr_code_from_data(mock_data)
    assert chan.dimension.value == dim
    assert chan.element_limit.value == dim


@pytest.mark.parametrize(("name", "dim", "prev_dim"), (("time", [1], [30]), ("amplitude", [10], [1])))
def test_setting_dimension_from_data_mismatched_dimension(chan: ChannelObject, mock_data: NumpyInterface, name: str,
                                                          dim: list[int], prev_dim: list[int],
                                                          caplog: LogCaptureFixture):
    """Test that if dimension from data does not match the previously set one, a warning is included in logs."""

    chan.name = name
    chan.dimension.value = prev_dim
    chan.set_dimension_and_repr_code_from_data(mock_data)
    assert chan.dimension.value == dim
    assert "Previously defined dimension" in caplog.text


@pytest.mark.parametrize(("name", "dim", "prev_dim"), (("time", [1], [0]), ("radius", [12], [10])))
def test_setting_dimension_from_data_mismatched_element_limit(chan: ChannelObject, mock_data: NumpyInterface, name: str, 
                                                              dim: list[int], prev_dim: list[int], 
                                                              caplog: LogCaptureFixture):
    """Test that if element limit from data does not match the previously set one, a warning is included in logs."""

    chan.name = name
    chan.element_limit.value = prev_dim
    chan.set_dimension_and_repr_code_from_data(mock_data)
    assert chan.element_limit.value == dim
    assert "Previously defined element limit" in caplog.text


