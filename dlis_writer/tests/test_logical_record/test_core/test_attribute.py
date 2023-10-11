import pytest

from dlis_writer.logical_record.core.attribute import Attribute
from dlis_writer.utils.enums import Units, RepresentationCode


@pytest.fixture
def attr():
    yield Attribute('some_attribute')


@pytest.mark.parametrize(("val", "unit"), (("m", Units.m), ("meter", Units.m), ("in_", Units.in_), ("inch", Units.in_)))
def test_setting_unit(attr, val, unit):
    attr.units = val
    assert attr.units is unit


def test_clearing_unit(attr):
    attr.units = None
    assert attr.units is None


@pytest.mark.parametrize(("val", "repr_code"), (
        (2, RepresentationCode.FSINGL),
        ("FSINGL", RepresentationCode.FSINGL),
        ("UNITS", RepresentationCode.UNITS),
        ('27', RepresentationCode.UNITS)
))
def test_setting_repr_code(attr, val, repr_code):
    attr.representation_code = val
    assert attr.representation_code is repr_code


def test_clearing_repr_code(attr):
    attr.representation_code = None
    assert attr.representation_code is None
