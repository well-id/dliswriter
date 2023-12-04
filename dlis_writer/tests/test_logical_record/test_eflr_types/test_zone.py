import pytest
from datetime import datetime
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.zone import Zone, ZoneObject
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.tests.common import base_data_path, config_params


@pytest.mark.parametrize("zone_nr", (1, 2, 3, 4))
def test_from_config(config_params: ConfigParser, zone_nr: int):
    """Test creating ZoneObject from config."""

    key = f"Zone-{zone_nr}"
    zone: ZoneObject = Zone.make_object_from_config(config_params, key=key)
    
    conf = config_params[key]
    
    assert zone.name == conf['name']
    assert zone.description.value == conf['description']
    assert zone.domain.value == conf['domain']
    
    assert isinstance(zone.maximum.representation_code, RepresentationCode)
    assert isinstance(zone.minimum.representation_code, RepresentationCode)

    if zone_nr != 3:
        assert isinstance(zone.maximum.units, str)
        assert zone.maximum.units == conf['maximum.units']
        assert isinstance(zone.minimum.units, str)
        assert zone.minimum.units == conf['minimum.units']


@pytest.mark.parametrize(("zone_nr", "value_type", "repr_code"), (
        (1, float, RepresentationCode.FDOUBL),
        (2, float, RepresentationCode.FDOUBL),
        (3, datetime, RepresentationCode.DTIME)
))
def test_from_config_units(config_params: ConfigParser, zone_nr: int, value_type: type, repr_code: RepresentationCode):
    """Test creating ZoneObject from config for different types of values. Check that the repr code is correct."""

    key = f"Zone-{zone_nr}"
    zone: ZoneObject = Zone.make_object_from_config(config_params, key=key)

    assert isinstance(zone.maximum.value, value_type)
    assert isinstance(zone.minimum.value, value_type)

    assert zone.maximum.representation_code is repr_code
    assert zone.minimum.representation_code is repr_code

