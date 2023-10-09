import pytest

from dlis_writer.logical_record.eflr_types import Channel
from dlis_writer.utils.enums import RepresentationCode, Units
from dlis_writer.tests.common import base_data_path, config_params, make_config_for_object


def test_from_config(config_params):
    channel = Channel.from_config(config_params)

    assert channel.object_name == config_params['Channel']['name']
    assert channel.name == config_params['Channel']['name']

    conf = config_params['Channel.attributes']
    assert channel.long_name.value == conf["long_name"]
    assert channel.properties.value == ["property1", "property 2 with multiple words"]
    assert channel.representation_code.value is RepresentationCode.FSINGL
    assert channel.units.value is Units.acre
    assert channel.dimension.value == 12
    assert channel.axis.value == 'some axis'
    assert channel.element_limit.value == 12
    assert channel.source.value == 'some source'
    assert channel.minimum_value.value == 0.
    assert isinstance(channel.minimum_value.value, float)
    assert channel.maximum_value.value == 127.6


def test_properties():
    pass  # TODO


def test_dimension_and_element_limit():
    pass  # TODO


def test_multiple_channels():
    pass  # TODO




