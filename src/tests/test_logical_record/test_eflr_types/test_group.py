import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.group import GroupSet, GroupItem
from dlis_writer.logical_record.eflr_types.channel import ChannelItem
from dlis_writer.logical_record.eflr_types.process import ProcessItem

from tests.common import base_data_path, config_params


@pytest.mark.parametrize(("key", "name", "description", "object_type", "object_class", "object_names", "group_names"), (
        ("1", "ChannelGroup", "Group of channels", "CHANNEL", ChannelItem, ["Channel 1", "Channel 2"], []),
        ("2", "ProcessGroup", "Group of processes", "PROCESS", ProcessItem, ["Process 1", "Prc2"], []),
        ("3", "MultiGroup", "Group of groups", "GROUP", None, [], ["ChannelGroup", "ProcessGroup"])
))
def test_group_params(config_params: ConfigParser, key: str, name: str, description: str, object_type: str,
                      object_class: type, object_names: list[str], group_names: list[str]):
    """Test creating GroupObject from config."""

    g: GroupItem = GroupItem.from_config(config_params, f"Group-{key}")

    assert g.name == name
    assert g.description.value == description
    assert g.object_type.value == object_type

    for i, name in enumerate(object_names):
        assert g.object_list.value[i].name == name
        assert isinstance(g.object_list.value[i], object_class)

    for i, name in enumerate(group_names):
        assert g.group_list.value[i].name == name
        assert isinstance(g.group_list.value[i], GroupItem)

