import os
import pytest
from pathlib import Path

from dlis_writer.utils.loaders import load_hdf5
from dlis_writer.tests.utils.mwe_dlis_creation import write_dlis_file
from dlis_writer.tests.utils.compare_dlis_files import compare


@pytest.fixture
def base_data_path():
    return Path(__file__).resolve().parent


@pytest.fixture
def h5_data_file_path(base_data_path):
    return base_data_path / 'resources/mock_data.hdf5'


@pytest.fixture
def reference_dlis_path(base_data_path):
    return base_data_path / 'resources/reference_mock_dlis.DLIS'


@pytest.fixture
def new_dlis_path(base_data_path):
    new_path = base_data_path/'outputs/new_fake_dlis.DLIS'
    os.makedirs(new_path.parent, exist_ok=True)
    yield new_path

    if new_path.exists():  # does not exist if file creation failed
        os.remove(new_path)


def test_correct_dlis_contents(reference_dlis_path, new_dlis_path, h5_data_file_path):
    write_dlis_file(data=load_hdf5(h5_data_file_path), dlis_file_name=new_dlis_path)
    assert compare(reference_dlis_path, new_dlis_path, verbose=False)

