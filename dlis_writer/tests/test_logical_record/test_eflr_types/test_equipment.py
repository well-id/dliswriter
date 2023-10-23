import pytest

from dlis_writer.logical_record.eflr_types import Equipment
from dlis_writer.utils.enums import Units
from dlis_writer.tests.common import base_data_path, config_params


@pytest.mark.parametrize(("idx", "section", "name", "status", "serial_number"), (
        (0, "Equipment-1", "EQ1", 1, "9101-21391"),
        (1, "Equipment-2", "EQ2", 0, "5559101-21391"),
        (2, "Equipment-X", "EqX", 1, "12311")
))
def test_from_config(config_params, idx, section, name, status, serial_number):
    eq = Equipment.make_from_config(config_params, key=section)

    assert eq.name == name
    assert eq.status.value == status
    assert isinstance(eq.status.value, int)
    assert eq.serial_number.value == serial_number
    assert isinstance(eq.serial_number.value, str)


def test_from_config_params_and_units(config_params):
    eq = Equipment.make_from_config(config_params, key="Equipment-1")

    def check(name, val, unit):
        attr = getattr(eq, name)
        assert attr.value == val
        assert attr.units is unit

    check('height', 140, Units.in_)
    check('length', 230.78, Units.cm)
    check('minimum_diameter', 2.3, Units.m)
    check('maximum_diameter', 3.2, Units.m)
    check('volume', 100, Units.cm3)
    check('weight', 1.2, Units.t)
    check('hole_size', 323.2, Units.m)
    check('pressure', 18000, Units.psi)
    check('temperature', 24, Units.degC)
    check('vertical_depth', 587, Units.m)
    check('radial_drift', 23.22, Units.m)
    check('angular_drift', 32.5, Units.m)



