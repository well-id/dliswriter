from dlisio import dlis    # type: ignore  # untyped library


def test_frame(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of Frame in the new DLIS file."""

    assert len(short_dlis.frames) == 1

    frame = short_dlis.frames[0]

    assert frame.name == "MAIN FRAME"
    assert frame.index_type == "TIME"
    assert frame.origin == 42
