import pytest

from dlis_writer.logical_record.eflr_types import LongName
from dlis_writer.tests.common import base_data_path, config_params, make_config


def test_from_config(config_params):
    w = LongName.make_from_config(config_params, 'LongName-1')
    t = 'SOME ASCII TEXT'

    assert w.general_modifier.value == [t]
    assert w.quantity.value == t
    assert w.quantity_modifier.value == [t]
    assert w.altered_form.value == t
    assert w.entity.value == t
    assert w.entity_modifier.value == [t]
    assert w.entity_number.value == t
    assert w.entity_part.value == t
    assert w.entity_part_number.value == t
    assert w.generic_source.value == t
    assert w.source_part.value == [t]
    assert w.source_part_number.value == [t]
    assert w.conditions.value == [t]
    assert w.standard_symbol.value == t
    assert w.private_symbol.value == t