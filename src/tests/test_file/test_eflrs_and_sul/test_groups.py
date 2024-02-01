import pytest
from dlisio import dlis    # type: ignore  # untyped library

from tests.common import check_list_of_objects


@pytest.mark.parametrize(("idx", "name", "description", "object_names", "group_names"), (
        (0, "ChannelGroup", "Group of channels", ["Channel 1", "Channel 2"], []),
        (1, "ProcessGroup", "Group of processes", ["Process 1", "Prc2"], []),
        (2, "MultiGroup", "Group of groups", [], ["ChannelGroup", "ProcessGroup"]),
        (3, "Mixed-group", "Mixed objects", ["posix time", "surface rpm", "Prc2"], ["ChannelGroup", "MultiGroup"])
))
def test_group_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, description: str,
                      object_names: list[str], group_names: list[str]) -> None:
    """Test attributes of Group objects in the DLIS file."""

    g = short_dlis.groups[idx]
    assert g.name == name
    assert g.description == description
    assert g.origin == 42
    check_list_of_objects(g.objects, object_names)
    check_list_of_objects(g.groups, group_names)
