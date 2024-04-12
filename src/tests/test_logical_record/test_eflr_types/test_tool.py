import pytest

from dliswriter.logical_record.eflr_types.tool import ToolSet, ToolItem


@pytest.mark.parametrize(("name", "description", "status", "param_names", "channel_names"), (
        ("TOOL-1", "SOME TOOL", 1, ["param3", "param2"], ["channel1", "channel2"]),
        ("Tool-X", "desc", 0, ["param1"], ["chan"])
))
def test_creating_tool(name: str, description: str, status: int, param_names: list[str], channel_names: list[str],
                       request: pytest.FixtureRequest) -> None:
    """Test creating ToolItem."""

    tool = ToolItem(
        name,
        description=description,
        status=status,
        parameters=[request.getfixturevalue(v) for v in param_names],
        channels=[request.getfixturevalue(v) for v in channel_names],
        parent=ToolSet()
    )

    assert tool.name == name
    assert tool.description.value == description
    assert tool.status.value == status

    for i, pn in enumerate(param_names):
        assert tool.parameters.value[i] is request.getfixturevalue(pn)

    for i, cn in enumerate(channel_names):
        assert tool.channels.value[i] is request.getfixturevalue(cn)

    assert isinstance(tool.parent, ToolSet)
    assert tool.parent.set_name is None
