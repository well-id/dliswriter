import pytest

from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.tests.common import base_data_path, config_params, make_config_for_object


def _check_with_config(sul, config):
    assert sul.set_identifier == config['StorageUnitLabel']['name']
    assert sul.sequence_number == int(config['StorageUnitLabel']['sequence_number'])


def test_from_config(config_params):
    sul = StorageUnitLabel.from_config(config_params)
    _check_with_config(sul, config_params)


@pytest.mark.parametrize(("name", "sequence_number"), (("SUL-1", "11"), ("Default storage", "0")))
def test_from_config_with_params(name, sequence_number):
    config = make_config_for_object("StorageUnitLabel", add_attributes=False)
    config["StorageUnitLabel"]["name"] = name
    config["StorageUnitLabel"]["sequence_number"] = sequence_number

    sul = StorageUnitLabel.from_config(config)
    _check_with_config(sul, config)
