import pytest

from dlis_writer.logical_record.eflr_types.axis import AxisItem, AxisSet
from dlis_writer import high_compatibility_mode_decorator


@pytest.mark.parametrize(('name', 'axis_id', 'units'), (
    ('Axis-1', 'First axis', 'm'),
    ('Axis-X', 'Another axis', 's')
))
def test_str_attributes(name: str, axis_id: str, units: str) -> None:
    axis = AxisItem(name, axis_id=axis_id, spacing={'units': units}, parent=AxisSet())

    assert axis.name == name
    assert axis.axis_id.value == axis_id
    assert axis.spacing.units == units


@pytest.mark.parametrize(('given', 'expected'), (
        ([40.395241, 27.792471], [40.395241, 27.792471]),
        (12.121, [12.121]),
        ([8], [8])
))
def test_coordinates(given: list, expected: list) -> None:
    axis = AxisItem('some_name', coordinates=given, parent=AxisSet())
    assert axis.coordinates.value == expected


def test_copy_numbers() -> None:
    parent = AxisSet()

    for i in range(5):
        ax = AxisItem('XYZ', parent=parent)
        assert ax.copy_number == i


@pytest.mark.parametrize("name", ("AXIS-1", "TIME_AXIS", "123"))
@high_compatibility_mode_decorator
def test_name_compatible(name: str) -> None:
    AxisItem(name, parent=AxisSet())  # no error = name accepted, test passed


@pytest.mark.parametrize("name", ("Axis 3", "NEW AXIS", "1.2A"))
@high_compatibility_mode_decorator
def test_name_not_compatible(name: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        AxisItem(name, parent=AxisSet())


@pytest.mark.parametrize("aid", ("SOME-AXIS", "AXIS_FOR_SPECIFIC_STUFF-124", "3112-1212"))
@high_compatibility_mode_decorator
def test_axis_id_compatible(aid: str) -> None:
    AxisItem("AX-1", axis_id=aid, parent=AxisSet())


@pytest.mark.parametrize("aid", ("The third axis", "AX FOR THINGS", "A.123"))
@high_compatibility_mode_decorator
def test_axis_id_not_compatible(aid: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        AxisItem("AXIS3", axis_id=aid, parent=AxisSet())
