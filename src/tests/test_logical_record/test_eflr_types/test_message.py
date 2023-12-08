from datetime import datetime
from configparser import ConfigParser
import pytest

from dlis_writer.logical_record.eflr_types.message import MessageTable, CommentTable, MessageItem, CommentItem

from tests.common import base_data_path, config_params


def test_message_from_config(config_params: ConfigParser):
    """Test creating MessageObject from config."""

    key = "Message-1"
    m: MessageItem = MessageTable.make_eflr_item_from_config(config_params, key=key)

    assert m.name == "MESSAGE-1"
    assert m._type.value == 'Command'
    assert m.time.value == datetime(2050, 3, 4, 11, 23, 11)
    assert m.borehole_drift.value == 123.34
    assert m.vertical_depth.value == 234.45
    assert m.radial_drift.value == 345.56
    assert m.angular_drift.value == 456.67
    assert m.text.value == ["Test message 11111"]


@pytest.mark.parametrize(("key", "name", "text"), (
        ("1", "COMMENT-1", ["SOME COMMENT HERE"]),
        ("other", "cmt2", ["some other comment here", "and another comment"])
))
def test_comment_from_config(config_params: ConfigParser, key: str, name: str, text: list[str]):
    """Test creating CommentObject from config."""

    key = f"Comment-{key}"
    c: CommentItem = CommentTable.make_eflr_item_from_config(config_params, key=key)

    assert c.name == name
    assert c.text.value == text
