import pytest
from dlisio import dlis    # type: ignore  # untyped library
from typing import Union

from tests.common import check_list_of_objects


def test_computation(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of Computation objects in the DLIS file matches the expected one."""

    comps = short_dlis.computations
    assert len(comps) == 3


@pytest.mark.parametrize(("idx", "name", "properties", "zone_names", "axis_name", "values"), (
        (0, "COMPT-1", ["LOCALLY-DEFINED", "AVERAGED"], ["Zone-1", "Zone-2"], "Axis-3", [[100, 200, 300], [1, 2, 3]]),
        (1, "COMPT2", ["UNDER-SAMPLED", "AVERAGED"], ["Zone-1", "Zone-3"], "Axis-4", [[1.5, 2.5], [4.5, 3.2]]),
        (2, "COMPT-X", ["OVER-SAMPLED"], [], "Axis-1", [list(range(12, 24))]),
))
def test_computation_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, properties: list[str],
                            zone_names: list[str], axis_name: str, values: list[Union[int, float]]) -> None:
    """Check attributes of Computation objects in the new DLIS file."""

    comp = short_dlis.computations[idx]

    assert comp.name == name
    assert comp.properties == properties
    assert comp.axis[0].name == axis_name
    assert comp.values.tolist() == values
    assert comp.origin == 42

    check_list_of_objects(comp.zones, zone_names)


def test_computation_long_name(short_dlis: dlis.file.LogicalFile) -> None:
    assert short_dlis.computations[0].long_name == "COMPT1"
    assert short_dlis.computations[1].long_name is short_dlis.longnames[0]
    assert short_dlis.computations[2].long_name == "Computation not added to process"
