import pytest

from dlis_writer.logical_record.eflr_types import NoFormat
from dlis_writer.tests.common import base_data_path, config_params, make_config


@pytest.mark.parametrize(("key", "name", "consumer_name", "description"), (
        ("1", "no_format_1", "SOME TEXT NOT FORMATTED", "TESTING-NO-FORMAT"),
        ("2", "no_fmt2", "xyz", "TESTING NO FORMAT 2")
))
def test_from_config(config_params, key, name, consumer_name, description):
    key = f"NoFormat-{key}"
    w = NoFormat.make_from_config(config_params, key=key)

    assert w._name == name
    assert w.consumer_name.value == consumer_name
    assert w.description.value == description

