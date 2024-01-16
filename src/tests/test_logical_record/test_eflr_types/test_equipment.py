import pytest
from typing import Any

from dlis_writer.logical_record.eflr_types.equipment import EquipmentSet, EquipmentItem


@pytest.mark.parametrize(("name", "status", "serial_number"), (
        ("EQ1", 1, "9101-21391"),
        ("EQ2", 0, "5559101-21391"),
        ("EqX", 1, "12311")
))
def test_creation(name: str, status: int, serial_number: str) -> None:
    """Check that EquipmentObject instances are correctly created from config."""

    eq = EquipmentItem(
        name,
        status=status,
        serial_number=serial_number
    )

    assert eq.name == name
    assert eq.status.value == status
    assert isinstance(eq.status.value, int)
    assert eq.serial_number.value == serial_number
    assert isinstance(eq.serial_number.value, str)

    assert isinstance(eq.parent, EquipmentSet)
    assert eq.parent.set_name is None


def test_params_and_units() -> None:
    """Check setting up EquipmentObject's parameters and units."""

    eq = EquipmentItem(
        "Equipment-1",
        **{
            'height': {'value': 140, 'units': 'in'},
            'length': {'value': 230.78, 'units': 'cm'},
            'minimum_diameter': {'value': 2.3, 'units': 'm'},
            'maximum_diameter': {'value': 3.2, 'units': 'm'},
            'weight': {'value': 1.2, 'units': 't'},
            'hole_size': {'value': 323.2, 'units': 'm'},
            'pressure': {'value': 18000, 'units': 'psi'},
            'temperature': {'value': 24, 'units': 'degC'},
            'vertical_depth': {'value': 587, 'units': 'm'},
            'radial_drift': {'value': 23.22, 'units': 'm'},
            'angular_drift': {'value': 32.5, 'units': 'm'}
        }
    )

    def check(name: str, val: Any, unit: str) -> None:
        attr = getattr(eq, name)
        assert attr.value == val
        assert attr.units == unit

    check('height', 140, 'in')
    check('length', 230.78, 'cm')
    check('minimum_diameter', 2.3, 'm')
    check('maximum_diameter', 3.2, 'm')
    check('weight', 1.2, 't')
    check('hole_size', 323.2, 'm')
    check('pressure', 18000, 'psi')
    check('temperature', 24, 'degC')
    check('vertical_depth', 587, 'm')
    check('radial_drift', 23.22, 'm')
    check('angular_drift', 32.5, 'm')
