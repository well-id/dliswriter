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
