import pytest

from dlis_writer.logical_record.eflr_types.computation import ComputationSet, ComputationItem
from dlis_writer.logical_record.eflr_types.axis import AxisItem
from dlis_writer.logical_record.eflr_types.zone import ZoneItem


@pytest.mark.parametrize(("name", "properties", "zone_names", "values"), (
        ("COMPT-1", ["LOCALLY-DEFINED", "AVERAGED"], ["Zone-1", "Zone-2", "Zone-3"], [100, 200, 300]),
        ("COMPT2", ["UNDER-SAMPLED", "AVERAGED"], ["Zone-1", "Zone-3"], [1.5, 2.5]),
        ("COMPT-X", ["OVER-SAMPLED"], ["Zone-3"], [12]),
))
def test_computation_creation(name: str, properties: list[str], zone_names: list[str], values: list, axis1: AxisItem,
                              zones: dict[str, ZoneItem]) -> None:
    """Check that ComputationObject instances are correctly created."""

    comp = ComputationItem(
        name,
        properties=properties,
        values=values,
        axis=axis1,
        zones=[v for k, v in zones.items() if k in zone_names],
        parent=ComputationSet()
    )

    assert comp.name == name
    assert comp.properties.value == properties
    assert comp.axis.value[0].name == axis1.name
    assert comp.values.value == values

    for i, n in enumerate(zone_names):
        assert comp.zones.value[i].name == n

    assert isinstance(comp.parent, ComputationSet)
    assert comp.parent.set_name is None
