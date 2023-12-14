import pytest

from dlis_writer.logical_record.eflr_types.equipment import EquipmentSet, EquipmentItem


@pytest.mark.parametrize(("name", "status", "serial_number"), (
        ("EQ1", 1, "9101-21391"),
        ("EQ2", 0, "5559101-21391"),
        ("EqX", 1, "12311")
))
def test_creation(name: str, status: int, serial_number: str):
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


def test_params_and_units():
    """Check setting up EquipmentObject's parameters and units."""

    eq = EquipmentItem(
        "Equipment-1",
        **{
            'height': 140,
            'height.units': 'in',
            'length': 230.78,
            'length.units': 'cm',
            'minimum_diameter': 2.3,
            'minimum_diameter.units': 'm',
            'maximum_diameter': 3.2,
            'maximum_diameter.units': 'm',
            'weight': 1.2,
            'weight.units': 't',
            'hole_size': 323.2,
            'hole_size.units': 'm',
            'pressure': 18000,
            'pressure.units': 'psi',
            'temperature': 24,
            'temperature.units': 'degC',
            'vertical_depth': 587,
            'vertical_depth.units': 'm',
            'radial_drift': 23.22,
            'radial_drift.units': 'm',
            'angular_drift': 32.5,
            'angular_drift.units': 'm'
        }
    )

    def check(name, val, unit):
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



