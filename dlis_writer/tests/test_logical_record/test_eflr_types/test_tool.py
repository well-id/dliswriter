import pytest

from dlis_writer.logical_record.eflr_types import Tool
from dlis_writer.tests.common import base_data_path, config_params


@pytest.mark.parametrize(("section", "name", "description", "status", "param_names", "channel_names"), (
        ("Tool-1", "TOOL-1", "SOME TOOL", 1, ["Param-1", "Param-3"], ["posix time", "amplitude"]),
        ("Tool-X", "Tool-X", "desc", 0, ["Param-2"], ["radius_pooh"])
))
def test_from_config(config_params, section, name, description, status, param_names, channel_names):
    tool = Tool.make_from_config(config_params, key=section)

    assert tool._name == name
    assert tool.description.value == description
    assert tool.status.value == status

    for i, pn in enumerate(param_names):
        assert tool.parameters.value[i]._name == pn

    for i, cn in enumerate(channel_names):
        assert tool.channels.value[i].name == cn
