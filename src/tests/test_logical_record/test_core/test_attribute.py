import pytest
from datetime import datetime, timedelta
from typing import Any, Generator

from dliswriter.logical_record.core.attribute import Attribute, DTimeAttribute


@pytest.fixture
def attr() -> Generator:
    """Basic mock attribute for tests."""

    yield Attribute('some_attribute')


@pytest.mark.parametrize(("val", "unit"), (("m", 'm'), ("in", 'in')))
def test_setting_unit(attr: Attribute, val: str, unit: str) -> None:
    """Test that attribute units are set correctly."""

    attr.units = val
    assert attr.units is unit


def test_clearing_unit(attr: Attribute) -> None:
    """Test that removing a previously defined unit works correctly."""

    attr.units = None
    assert attr.units is None


@pytest.mark.parametrize("dts", ("2050/03/21 15:30:00", "2003.12.31 09:30:00"))
def test_parse_dtime(dts: str) -> None:
    """Check that correctly formatted date-time strings are parsed correctly."""

    dt = DTimeAttribute.parse_dtime(dts)
    assert isinstance(dt, datetime)


@pytest.mark.parametrize("dts", ("2050/21/03 15:30:00", "2050.03.02 15:30"))
def test_parse_dtime_wrong_format(dts: str) -> None:
    """Check that a ValueError is raised if a provided date-time string does not follow any of the allowed formats."""

    with pytest.raises(ValueError, match=".*does not conform to any of the allowed formats.*"):
        DTimeAttribute.parse_dtime(dts)


@pytest.mark.parametrize("dts", (object(), timedelta(seconds=12)))
def test_parse_dtime_wrong_type(dts: Any) -> None:
    """Check that a TypeError is raised if the provided date-time string is not actually a string."""

    with pytest.raises(TypeError, match="Expected a str.*"):
        DTimeAttribute.parse_dtime(dts)
