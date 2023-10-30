import pytest
from datetime import datetime

from dlis_writer.logical_record.eflr_types import Zone
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.tests.common import base_data_path, config_params, make_config


@pytest.mark.parametrize("zone_nr", (1, 2, 3, 4))
def test_from_config(config_params, zone_nr):
    key = f"Zone-{zone_nr}"
    zone = Zone.make_from_config(config_params, key=key)
    
    conf = config_params[key]
    
    assert zone.name == conf['name']
    assert zone.description.value == conf['description']
    assert zone.domain.value == conf['domain']
    
    assert isinstance(zone.maximum.representation_code, RepresentationCode)
    assert isinstance(zone.minimum.representation_code, RepresentationCode)

    if zone_nr != 3:
        assert isinstance(zone.maximum.units, str)
        assert zone.maximum.units == conf['maximum.units'] or zone.maximum.units.name == conf['maximum.units']
        assert isinstance(zone.minimum.units, str)
        assert zone.minimum.units == conf['minimum.units'] or zone.minimum.units.name == conf['minimum.units']


@pytest.mark.parametrize(("zone_nr", "value_type", "repr_code"), (
        (1, float, RepresentationCode.FDOUBL),
        (2, float, RepresentationCode.FDOUBL),
        (3, datetime, RepresentationCode.DTIME)
))
def test_from_config_units(config_params, zone_nr, value_type, repr_code):
    key = f"Zone-{zone_nr}"
    zone = Zone.make_from_config(config_params, key=key)

    assert isinstance(zone.maximum.value, value_type)
    assert isinstance(zone.minimum.value, value_type)

    assert zone.maximum.representation_code is repr_code
    assert zone.minimum.representation_code is repr_code

