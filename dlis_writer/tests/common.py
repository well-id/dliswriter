import pytest
from pathlib import Path
from configparser import ConfigParser

from dlis_writer.writer.dlis_config import load_config
from dlis_writer.logical_record.eflr_types import eflr_types


def clear_eflr_instance_registers():
    """Remove all defined instances of EFLR from the internal dicts. Clear the EFLRObject dicts of the instances."""

    for eflr_type in eflr_types:
        for eflr in eflr_type.get_all_instances():
            eflr.clear_object_dict()
        eflr_type.clear_eflr_instance_dict()


@pytest.fixture(scope='session')
def base_data_path() -> Path:
    """Path to the resources files."""

    return Path(__file__).resolve().parent


@pytest.fixture(scope='session')
def config_params(base_data_path: Path) -> ConfigParser:
    """Config object with information on different DLIS objects to be included."""

    return load_config(base_data_path/'resources/mock_config_params.ini')


def make_config(*sections: str) -> ConfigParser:
    """Create a config object containing all sections whose names are specified as positional args."""

    config = ConfigParser()
    for section in sections:
        config.add_section(section)
    return config

