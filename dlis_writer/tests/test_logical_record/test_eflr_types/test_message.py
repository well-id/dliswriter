from datetime import datetime

import pytest

from dlis_writer.logical_record.eflr_types import Message, Comment
from dlis_writer.tests.common import base_data_path, config_params, make_config


def test_message_from_config(config_params):
    key = "Message-1"
    m = Message.make_from_config(config_params, key=key)

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
def test_comment_from_config(config_params, key, name, text):
    key = f"Comment-{key}"
    c = Comment.make_from_config(config_params, key=key)

    assert c.name == name
    assert c.text.value == text
