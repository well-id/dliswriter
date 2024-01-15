import pytest
from datetime import datetime
from typing import Union

from dlis_writer.logical_record.eflr_types.zone import ZoneSet, ZoneItem
from dlis_writer.utils.enums import RepresentationCode


@pytest.mark.parametrize(("name", "description", "domain", "maximum", "minimum", "m_type", "rc"), (
        ("Zone-1", "Zone 1", "VERTICAL-DEPTH", 100, 10, float, RepresentationCode.FDOUBL),
        ("Z2", "some zone", "BOREHOLE-DEPTH", -300.5, -500.0, float, RepresentationCode.FDOUBL),
        ("ZoneX", "time zone", "TIME", "2050/03/02 15:20:00", "2050/03/02 10:10:00", datetime, RepresentationCode.DTIME)
))
def test_zone_creation(name: str, description: str, domain: str, maximum: Union[int, float], minimum: Union[int, float],
                       m_type: type, rc: RepresentationCode) -> None:
    """Test creating ZoneObject from config."""

    zone = ZoneItem(
        name,
        description=description,
        domain=domain,
        maximum=maximum,
        minimum=minimum
    )

    assert zone.name == name
    assert zone.description.value == description
    assert zone.domain.value == domain

    assert zone.maximum.representation_code is rc
    assert zone.minimum.representation_code is rc

    assert isinstance(zone.maximum.value, m_type)
    assert isinstance(zone.minimum.value, m_type)

    assert isinstance(zone.parent, ZoneSet)
    assert zone.parent.set_name is None
