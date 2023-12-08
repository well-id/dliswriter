import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.computation import ComputationTable, ComputationItem

from tests.common import base_data_path, config_params


@pytest.mark.parametrize(("section", "name", "properties", "zone_names", "axis_name", "values"), (
        ("Computation-1", "COMPT-1", ["PROP 1", "AVERAGED"], ["Zone-1", "Zone-2", "Zone-3"], "Axis-1", [100, 200, 300]),
        ("Computation-2", "COMPT2", ["PROP 2", "AVERAGED"], ["Zone-1", "Zone-3"], "Axis-1", [1.5, 2.5]),
        ("Computation-X", "COMPT-X", ["XYZ"], ["Zone-3"], "Axis-1", [12]),
))
def test_from_config(config_params: ConfigParser, section: str, name: str, properties: list[str], zone_names: list[str],
                     axis_name: str, values: list):
    """Check that ComputationObject instances are correctly created from config."""

    comp: ComputationItem = ComputationTable.make_eflr_item_from_config(config_params, key=section)

    assert comp.name == name
    assert comp.properties.value == properties
    assert comp.axis.value.name == axis_name
    assert comp.values.value == values

    for i, n in enumerate(zone_names):
        assert comp.zones.value[i].name == n
