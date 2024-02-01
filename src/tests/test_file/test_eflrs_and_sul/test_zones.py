import pytest
from datetime import datetime
from dlisio import dlis    # type: ignore  # untyped library
from typing import Any
from pytz import utc


def test_zones(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of zones in the file matches the expected one."""

    zones = short_dlis.zones
    assert len(zones) == 5


@pytest.mark.parametrize(("name", "description", "maximum", "minimum", "value_type"), (
        ("Zone-1", "BOREHOLE-DEPTH-ZONE", 1300, 100, float),
        ("Zone-2", "VERTICAL-DEPTH-ZONE", 2300.45, 200, float),
        ("Zone-3", "ZONE-TIME", datetime(2050, 7, 13, 11, 30).astimezone(utc),
         datetime(2050, 7, 12, 9).astimezone(utc), datetime),
        ("Zone-4", "ZONE-TIME-2", 90, 10, float),
        ("Zone-X", "Zone not added to any parameter", 10, 1, float)
))
def test_zone_params(short_dlis: dlis.file.LogicalFile, name: str, description: str, maximum: Any,
                     minimum: Any, value_type: type) -> None:
    """Check attributes of zones in the new DLIS file."""

    zones = [zone for zone in short_dlis.zones if zone.name == name]
    assert len(zones) == 1
    z = zones[0]

    assert z.description == description

    assert isinstance(z.maximum, value_type)
    assert isinstance(z.minimum, value_type)

    z_maximum = z.maximum
    z_minimum = z.minimum

    if value_type is datetime:
        # dlisio doesn't add time zone info to the parsed datetime objects; utc.localize marks them as UTC
        z_maximum = utc.localize(z_maximum)  # type: ignore
        z_minimum = utc.localize(z_minimum)  # type: ignore

    assert z_maximum == maximum
    assert z_minimum == minimum

    assert z.origin == 42


def test_zone_not_in_param(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that a zone which has not been added to any parameter or other object is still in the file."""

    name = 'Zone-X'
    z = [z for z in short_dlis.zones if z.name == name]
    assert len(z) == 1
    for p in short_dlis.parameters:
        z = [z for z in p.zones if z.name == name]
        assert not z
