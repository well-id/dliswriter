import pytest
from contextlib import contextmanager
from dlisio import dlis

from dlis_writer.utils.loaders import load_hdf5
from dlis_writer.writer.writer import DLISWriter

from dlis_writer.tests.common import base_data_path


N_COLS = 128
SHORT_N_ROWS = 100


@pytest.fixture(scope='session')
def reference_data(base_data_path):
    return load_hdf5(base_data_path / 'resources/mock_data.hdf5')


@pytest.fixture(scope='session')
def short_reference_data(reference_data):
    return reference_data[:SHORT_N_ROWS]


@contextmanager
def load_dlis(fname):
    with dlis.load(fname) as (f, *tail):
        try:
            yield f
        finally:
            pass


def select_channel(f, name):
    return f.object("CHANNEL", name)


def write_dlis_file(data, dlis_file_name, config):
    writer = DLISWriter(data, config)
    writer.write_dlis_file(dlis_file_name=dlis_file_name)

