import pytest
from datetime import datetime, timedelta

from dlis_writer.logical_record.core.attribute import Attribute, DTimeAttribute
from dlis_writer.utils.enums import RepresentationCode


@pytest.fixture
def attr():
    yield Attribute('some_attribute')


@pytest.mark.parametrize(("val", "unit"), (("m", 'm'), ("meter", 'meter'), ("in", 'in'), ("inch", 'inch')))
def test_setting_unit(attr, val, unit):
    attr.units = val
    assert attr.units is unit


def test_clearing_unit(attr):
    attr.units = None
    assert attr.units is None


@pytest.mark.parametrize(("val", "repr_code"), (
        (2, RepresentationCode.FSINGL),
        ("FSINGL", RepresentationCode.FSINGL),
        ("STATUS", RepresentationCode.STATUS),
        ('26', RepresentationCode.STATUS)
))
def test_setting_repr_code(attr, val, repr_code):
    attr.representation_code = val
    assert attr.representation_code is repr_code


@pytest.mark.parametrize(("code1", "code2"), ((2, 3), (3, 2), (1, 1)))
def test_setting_repr_code_already_set(attr, code1, code2):
    attr.representation_code = code1
    with pytest.raises(RuntimeError, match="representation code .* is already set .*"):
        attr.representation_code = code2


@pytest.mark.parametrize("dts", ("2050/03/21 15:30:00", "2003.12.31 09:30:00"))
def test_parse_dtime(dts):
    dt = DTimeAttribute.parse_dtime(dts)
    assert isinstance(dt, datetime)


@pytest.mark.parametrize("dts", ("2050/21/03 15:30:00", "2050.03.02 15:30"))
def test_parse_dtime_wrong_format(dts):
    with pytest.raises(ValueError, match=".*does not conform to any of the allowed formats.*"):
        DTimeAttribute.parse_dtime(dts)


@pytest.mark.parametrize("dts", (object(), timedelta(seconds=12)))
def test_parse_dtime_wrong_type(dts):
    with pytest.raises(TypeError, match="Expected a str.*"):
        DTimeAttribute.parse_dtime(dts)
