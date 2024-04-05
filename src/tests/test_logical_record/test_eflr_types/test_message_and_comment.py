from datetime import datetime
import pytest

from dlis_writer.logical_record.eflr_types.message import MessageSet, MessageItem
from dlis_writer.logical_record.eflr_types.comment import CommentSet, CommentItem


def test_creating_message() -> None:
    """Test creating MessageObject."""

    m = MessageItem(
        name="MESSAGE-1",
        _type='Command',
        time="2050/03/04 11:23:11",
        borehole_drift=123.34,
        vertical_depth=234.45,
        radial_drift=345.56,
        angular_drift=456.67,
        text=["Test message 11111"],
        parent=MessageSet()
    )

    assert m.name == "MESSAGE-1"
    assert m._type.value == 'Command'
    assert m.time.value == datetime(2050, 3, 4, 11, 23, 11)
    assert m.borehole_drift.value == 123.34
    assert m.vertical_depth.value == 234.45
    assert m.radial_drift.value == 345.56
    assert m.angular_drift.value == 456.67
    assert m.text.value == ["Test message 11111"]

    assert isinstance(m.parent, MessageSet)
    assert m.parent.set_name is None


@pytest.mark.parametrize(("name", "text"), (
        ("COMMENT-1", ["SOME COMMENT HERE"]),
        ("cmt2", ["some other comment here", "and another comment"])
))
def test_creating_comment(name: str, text: list[str]) -> None:
    """Test creating CommentObject."""

    c = CommentItem(
        name=name,
        text=text,
        parent=CommentSet()
    )

    assert c.name == name
    assert c.text.value == text

    assert isinstance(c.parent, CommentSet)
    assert c.parent.set_name is None
