import pytest
from dlisio import dlis    # type: ignore  # untyped library


@pytest.mark.parametrize(("idx", "name", "consumer_name", "description"), (
        (0, "no_format_1", "SOME TEXT NOT FORMATTED", "TESTING-NO-FORMAT"),
        (1, "no_fmt2", "xyz", "TESTING NO FORMAT 2")
))
def test_no_format_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, consumer_name: str,
                          description: str) -> None:
    """Check attributes of NoFormat objects in the DLIS file."""

    w = short_dlis.noformats[idx]

    assert w.name == name
    assert w.consumer_name == consumer_name
    assert w.description == description
    assert w.origin == 42
