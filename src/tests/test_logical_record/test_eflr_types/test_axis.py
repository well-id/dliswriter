import pytest

from dlis_writer.logical_record.eflr_types.axis import AxisItem, AxisSet


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
