import pytest

from dlis_writer.logical_record.eflr_types.group import GroupSet, GroupItem
from dlis_writer.logical_record.eflr_types.channel import ChannelItem
from dlis_writer.logical_record.eflr_types.process import ProcessItem
from dlis_writer.logical_record.core.eflr import EFLRItem


@pytest.mark.parametrize(("name", "description", "object_type", "object_class", "object_names", "group_names"), (
        ("ChannelGroup", "Group of channels", "CHANNEL", ChannelItem, ['channel1', 'channel2'], []),
        ("ProcessGroup", "Group of processes", "PROCESS", ProcessItem, ["process1", "process2"], []),
        ("MultiGroup", "Group of groups", "GROUP", None, [], ["channel_group", "process_group"])
))
def test_group_params(name: str, description: str, object_type: str,
                      object_class: type[EFLRItem], object_names: list[str], group_names: list[str],
                      request: pytest.FixtureRequest) -> None:
    """Test creating GroupItem."""

    g = GroupItem(
        name,
        description=description,
        object_type=object_type,
        object_list=[request.getfixturevalue(v) for v in object_names],
        group_list=[request.getfixturevalue(v) for v in group_names],
        parent=GroupSet()
    )

    assert g.name == name
    assert g.description.value == description
    assert g.object_type.value == object_type

    assert len(g.object_list.value) == len(object_names)
    for i, obj in enumerate(g.object_list.value):
        assert isinstance(obj, object_class)
        assert obj is request.getfixturevalue(object_names[i])

    assert len(g.group_list.value) == len(group_names)
    for i, grp in enumerate(g.group_list.value):
        assert isinstance(grp, GroupItem)
        assert grp is request.getfixturevalue(group_names[i])

    assert isinstance(g.parent, GroupSet)
    assert g.parent.set_name is None
