import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.tests.common import base_data_path, config_params, make_config


def _check_with_config(sul: StorageUnitLabel, config: ConfigParser):
    """Test that the parameters of the storage unit label are as expected."""

    assert sul.set_identifier == config['StorageUnitLabel']['name']
    assert sul.sequence_number == int(config['StorageUnitLabel']['sequence_number'])


def test_from_config(config_params: ConfigParser):
    """Test creating StorageUnitLabel from config."""

    sul = StorageUnitLabel.make_from_config(config_params)
    _check_with_config(sul, config_params)


@pytest.mark.parametrize(("name", "sequence_number"), (("SUL-1", "11"), ("Default storage", "0")))
def test_from_config_with_params(name: str, sequence_number: str):
    """Test creating StorageUnitLabel from config with alternative parameters."""

    config = make_config("StorageUnitLabel")
    config["StorageUnitLabel"]["name"] = name
    config["StorageUnitLabel"]["sequence_number"] = sequence_number

    sul = StorageUnitLabel.make_from_config(config)
    _check_with_config(sul, config)
