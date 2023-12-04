import pytest
from datetime import datetime, timedelta
from typing import Union, Any

from dlis_writer.logical_record.core.attribute import Attribute, DTimeAttribute
from dlis_writer.utils.enums import RepresentationCode


@pytest.fixture
def attr():
    """Basic mock attribute for tests."""

    yield Attribute('some_attribute')


@pytest.mark.parametrize(("val", "unit"), (("m", 'm'), ("in", 'in')))
def test_setting_unit(attr: Attribute, val: str, unit: str):
    """Test that attribute units are set correctly."""

    attr.units = val
    assert attr.units is unit


def test_clearing_unit(attr: Attribute):
    """Test that removing a previously defined unit works correctly."""

    attr.units = None
    assert attr.units is None


@pytest.mark.parametrize(("val", "repr_code"), (
        (2, RepresentationCode.FSINGL),
        ("FSINGL", RepresentationCode.FSINGL),
        ("STATUS", RepresentationCode.STATUS),
        ('26', RepresentationCode.STATUS)
))
def test_setting_repr_code(attr: Attribute, val: Union[int, str], repr_code: RepresentationCode):
    """Test that setting representation code works correctly, both from code name and value (as int or str)."""

    attr.representation_code = val  # type: ignore  # mypy property setter bug
    assert attr.representation_code is repr_code


@pytest.mark.parametrize(("code1", "code2"), ((2, 3), (3, 2), (1, 8)))
def test_setting_repr_code_already_set(attr: Attribute, code1: int, code2: int):
    """Check that a RuntimeError is raised if an attempt to change an already set representation code is made."""

    attr.representation_code = code1  # type: ignore  # mypy property setter bug
    with pytest.raises(RuntimeError, match="representation code .* is already set .*"):
        attr.representation_code = code2  # type: ignore  # mypy property setter bug


@pytest.mark.parametrize("dts", ("2050/03/21 15:30:00", "2003.12.31 09:30:00"))
def test_parse_dtime(dts: str):
    """Check that correctly formatted date-time strings are parsed correctly."""

    dt = DTimeAttribute.parse_dtime(dts)
    assert isinstance(dt, datetime)


@pytest.mark.parametrize("dts", ("2050/21/03 15:30:00", "2050.03.02 15:30"))
def test_parse_dtime_wrong_format(dts: str):
    """Check that a ValueError is raised if a provided date-time string does not follow any of the allowed formats."""

    with pytest.raises(ValueError, match=".*does not conform to any of the allowed formats.*"):
        DTimeAttribute.parse_dtime(dts)


@pytest.mark.parametrize("dts", (object(), timedelta(seconds=12)))
def test_parse_dtime_wrong_type(dts: Any):
    """Check that a TypeError is raised if the provided date-time string is not actually a string."""

    with pytest.raises(TypeError, match="Expected a str.*"):
        DTimeAttribute.parse_dtime(dts)
