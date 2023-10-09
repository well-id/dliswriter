import pytest
from pathlib import Path

from dlis_writer.utils.loaders import load_config


@pytest.fixture(scope='session')
def base_data_path():
    return Path(__file__).resolve().parent


@pytest.fixture(scope='session')
def config_params(base_data_path):
    return load_config(base_data_path/'resources/mock_config_params.ini')


