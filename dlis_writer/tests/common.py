import pytest
from pathlib import Path
from configparser import ConfigParser

from dlis_writer.utils.loaders import load_config
from dlis_writer.logical_record.eflr_types import eflr_types


def clear_eflr_instance_registers():
    for eflr_type in eflr_types:
        eflr_type.clear_eflr_instance_dict()


@pytest.fixture(scope='session')
def base_data_path():
    return Path(__file__).resolve().parent


@pytest.fixture(scope='session')
def config_params(base_data_path):
    return load_config(base_data_path/'resources/mock_config_params.ini')


def make_config(*sections):
    config = ConfigParser()
    for section in sections:
        config.add_section(section)
    return config

