from dlisio import dlis    # type: ignore  # untyped library


def test_storage_unit_label(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of Storage Unit Label in the new DLIS file."""

    sul = short_dlis.storage_label()
    assert sul['id'].rstrip(' ') == "DEFAULT STORAGE SET"
    assert sul['sequence'] == 1
    assert sul['maxlen'] == 8192
