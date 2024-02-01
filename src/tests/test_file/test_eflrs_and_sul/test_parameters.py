import pytest
from dlisio import dlis    # type: ignore  # untyped library
from typing import Union

from tests.common import check_list_of_objects


def test_parameters(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of parameters in the DLIS file matches the expected one."""

    params = short_dlis.parameters
    assert len(params) == 3


@pytest.mark.parametrize(("idx", "name", "long_name", "values", "zones"), (
        (0, "Param-1", "LATLONG-GPS", ["40deg 23' 42.8676'' N", "40deg 23' 42.8676'' N"], ["Zone-1", "Zone-3"]),
        (1, "Param-2", "LATLONG", [[40.395241, 27.792471, 21.23131213], [21, 23, 24]], ["Zone-2", "Zone-4"]),
        (2, "Param-3", None, [12.5], [])
))
def test_parameters_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, long_name: Union[str, None],
                           values: list, zones: list[str]) -> None:
    """Check attributes of DLIS Parameter objects."""

    if long_name is None:
        long_name = short_dlis.longnames[0]

    param = short_dlis.parameters[idx]
    assert param.name == name
    assert param.long_name == long_name
    assert param.values.tolist() == values
    assert param.origin == 42

    check_list_of_objects(param.zones, zones)
