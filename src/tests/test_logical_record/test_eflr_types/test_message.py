from datetime import datetime
import pytest

from dlis_writer.logical_record.eflr_types.message import MessageSet, CommentSet, MessageItem, CommentItem


def test_creating_message():
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
def test_creating_comment(name: str, text: list[str]):
    """Test creating CommentObject."""

    c = CommentItem(
        name=name,
        text=text
    )

    assert c.name == name
    assert c.text.value == text

    assert isinstance(c.parent, CommentSet)
    assert c.parent.set_name is None
