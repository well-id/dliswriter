import pytest
from datetime import datetime
from dlisio import dlis    # type: ignore  # untyped library
from pytz import utc


def test_message_params(short_dlis: dlis.file.LogicalFile) -> None:
    """Check attribute of Message object in the DLIS file."""

    m = short_dlis.messages[0]

    assert m.name == "MESSAGE-1"
    assert m.message_type == 'Command'
    assert utc.localize(m.time) == datetime(2050, 3, 4, 11, 23, 11).astimezone(utc)
    assert m.borehole_drift == 123.34
    assert m.vertical_depth == 234.45
    assert m.radial_drift == 345.56
    assert m.angular_drift == 456.67
    assert m.text == ["Test message 11111"]
    assert m.origin == 42


@pytest.mark.parametrize(("idx", "name", "text"), (
        (0, "COMMENT-1", ["SOME COMMENT HERE"]),
        (1, "cmt2", ["some other comment here", "and another comment"])
))
def test_comment_params(short_dlis: dlis.file.LogicalFile, idx: int, name: str, text: str) -> None:
    """Test attributes of Comment objects in the DLIS file."""

    c = short_dlis.comments[idx]

    assert c.name == name
    assert c.text == text
    assert c.origin == 42

