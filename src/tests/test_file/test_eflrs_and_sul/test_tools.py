import pytest
from dlisio import dlis    # type: ignore  # untyped library

from tests.common import check_list_of_objects


def test_tool(short_dlis: dlis.file.LogicalFile) -> None:
    tools = short_dlis.tools
    assert len(tools) == 2


@pytest.mark.parametrize(("idx", "name", "description", "status", "param_names", "channel_names"), (
        (0, "TOOL-1", "SOME TOOL", 1, ["Param-1", "Param-3"], ["posix time", "amplitude"]),
        (1, "Tool-X", "desc", 0, ["Param-2"], ["radius_pooh"])
))
def test_tool_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, description: str, status: int,
                     param_names: list[str], channel_names: list[str]) -> None:
    tool = short_dlis.tools[idx]
    assert tool.name == name
    assert tool.description == description
    assert tool.status == status
    assert tool.origin == 42

    check_list_of_objects(tool.parameters, param_names)
    check_list_of_objects(tool.channels, channel_names)
