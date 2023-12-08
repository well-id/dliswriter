import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.no_format import NoFormatTable, NoFormatItem

from tests.common import base_data_path, config_params


@pytest.mark.parametrize(("key", "name", "consumer_name", "description"), (
        ("1", "no_format_1", "SOME TEXT NOT FORMATTED", "TESTING-NO-FORMAT"),
        ("2", "no_fmt2", "xyz", "TESTING NO FORMAT 2")
))
def test_from_config(config_params: ConfigParser, key: str, name: str, consumer_name: str, description: str):
    """Test creating NoFormatObject from config."""

    key = f"NoFormat-{key}"
    w: NoFormatItem = NoFormatTable.make_object_from_config(config_params, key=key)

    assert w.name == name
    assert w.consumer_name.value == consumer_name
    assert w.description.value == description

