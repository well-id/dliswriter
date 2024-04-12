import pytest
from typing import Optional

from dliswriter.logical_record.eflr_types.path import PathItem, PathSet
from dliswriter.logical_record.eflr_types.frame import FrameItem
from dliswriter.logical_record.eflr_types.well_reference_point import WellReferencePointItem


@pytest.mark.parametrize(("name", "frm", "value", "wrp", "vertical_depth", "time"), (
        ("Path 1", "frame", ["channel1", "channel3"], "well_reference_point", 10., 12.5),
        ("PATH2", None, ["channel2"], None, -123.9, 277.),
))
def test_path_params(name: str, frm: Optional[str], value: list[str], wrp: Optional[str],
                     vertical_depth: float, time: float, request: pytest.FixtureRequest,
                     frame: FrameItem, well_reference_point: WellReferencePointItem) -> None:
    """Test creating PathItem."""

    path = PathItem(
        name,
        frame_type=request.getfixturevalue(frm) if frm else None,
        value=[request.getfixturevalue(v) for v in value],
        well_reference_point=request.getfixturevalue(wrp) if wrp else None,
        vertical_depth=vertical_depth,
        time=time,
        parent=PathSet()
    )

    assert path.name == name

    for i, n in enumerate(value):
        assert path.value.value[i] is request.getfixturevalue(value[i])

    if frm is not None:
        assert path.frame_type.value is frame

    if wrp is not None:
        assert path.well_reference_point.value is well_reference_point

    assert isinstance(path.parent, PathSet)
    assert path.parent.set_name is None
