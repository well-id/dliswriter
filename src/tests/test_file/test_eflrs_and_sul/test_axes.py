import pytest
from dlisio import dlis    # type: ignore  # untyped library


def test_axes(short_dlis: dlis.file.LogicalFile) -> None:
    """Check that the number of axes in the DLIS file matches the expected one."""

    axes = short_dlis.axes
    assert len(axes) == 4


@pytest.mark.parametrize(("idx", "name", "axis_id", "coordinates"), (
        (0, "Axis-1", "First axis", list(range(12))),
        (1, "Axis-X", "Axis not added to computation", [8])
))
def test_axes_parameters(short_dlis: dlis.file.LogicalFile, idx: int, name: str, axis_id: str,
                         coordinates: list) -> None:
    """Check attributes of axes in the DLIS file."""

    axis = short_dlis.axes[idx]
    assert axis.name == name
    assert axis.axis_id == axis_id
    assert axis.coordinates == coordinates
    assert axis.origin == 42
