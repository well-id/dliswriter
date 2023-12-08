import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.tooltable import ToolTable, ToolItem

from tests.common import base_data_path, config_params


@pytest.mark.parametrize(("section", "name", "description", "status", "param_names", "channel_names"), (
        ("Tool-1", "TOOL-1", "SOME TOOL", 1, ["Param-1", "Param-3"], ["posix time", "amplitude"]),
        ("Tool-X", "Tool-X", "desc", 0, ["Param-2"], ["radius_pooh"])
))
def test_from_config(config_params: ConfigParser, section: str, name: str, description: str, status: int,
                     param_names: list[str], channel_names: list[str]):
    """Test creating ToolObject from config."""

    tool: ToolItem = ToolTable.make_object_from_config(config_params, key=section)

    assert tool.name == name
    assert tool.description.value == description
    assert tool.status.value == status

    for i, pn in enumerate(param_names):
        assert tool.parameters.value[i].name == pn

    for i, cn in enumerate(channel_names):
        assert tool.channels.value[i].name == cn
