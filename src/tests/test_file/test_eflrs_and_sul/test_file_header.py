from dlisio import dlis    # type: ignore  # untyped library


def test_file_header(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attributes of DLIS file header."""

    header = short_dlis.fileheader
    assert header.id == "DEFAULT FHLR"
    assert header.sequencenr == "1"
    assert header.origin == 42
