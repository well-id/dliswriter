import pytest
from dlisio import dlis    # type: ignore  # untyped library

from tests.common import check_list_of_objects


def test_process(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of Process objects in the DLIS file matches the expected one."""

    procs = short_dlis.processes
    assert len(procs) == 2


@pytest.mark.parametrize(("idx", "name", "input_channels", "output_channels", "input_compts", "output_compts"), (
        (0, "Process 1", ["radius"], ["amplitude", "Channel 2"], ["COMPT-1"], ["COMPT2"]),
        (1, "Prc2", ["Channel 1"], ["Channel 2"], ["COMPT2", "COMPT-1"], []),
))
def test_process_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, input_channels: list[str],
                        output_channels: list[str], input_compts: list[str], output_compts: list[str]) -> None:
    """Check attributes of Process objects in the new DLIS file."""

    proc = short_dlis.processes[idx]

    assert proc.name == name
    assert proc.origin == 42

    check_list_of_objects(proc.input_channels, input_channels)
    check_list_of_objects(proc.output_channels, output_channels)
    check_list_of_objects(proc.input_computations, input_compts)
    check_list_of_objects(proc.output_computations, output_compts)
