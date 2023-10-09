import pytest
from pathlib import Path
from configparser import ConfigParser

from dlis_writer.utils.loaders import load_config


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


def make_config_for_object(name, add_attributes=True):
    sections = (name, f"{name}.attributes") if add_attributes else (name,)
    return make_config(*sections)
