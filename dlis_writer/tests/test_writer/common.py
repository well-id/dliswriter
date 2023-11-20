import numpy as np
import pytest
from contextlib import contextmanager
from dlisio import dlis
from pathlib import Path
import h5py

from dlis_writer.utils.loaders import load_hdf5
from dlis_writer.writer.writer import DLISWriter
from dlis_writer.utils.source_data_objects import NumpyInterface, HDF5Interface, SourceDataObject

from dlis_writer.tests.common import base_data_path, clear_eflr_instance_registers


N_COLS = 128


@pytest.fixture(scope='session')
def reference_data_path(base_data_path):
    return base_data_path / 'resources/mock_data.hdf5'


@pytest.fixture(scope='session')
def reference_data(reference_data_path):
    f = h5py.File(reference_data_path, 'r')
    yield f
    f.close()


@pytest.fixture(scope='session')
def short_reference_data_path(base_data_path):
    return base_data_path / 'resources/mock_data_short.hdf5'


@pytest.fixture(scope='session')
def short_reference_data(short_reference_data_path):
    f = h5py.File(short_reference_data_path, 'r')
    yield f
    f.close()


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
    clear_eflr_instance_registers()

    if isinstance(data, np.ndarray):
        data = NumpyInterface.from_config(data, config)
    elif isinstance(data, (str, Path)):
        data = HDF5Interface.from_config(data, config)
    elif not isinstance(data, SourceDataObject):
        raise TypeError(f"Expected a SourceDataObject, numpy.ndarray, or a path to a HDF5 file; got {type(data)}")

    writer = DLISWriter(data, config)
    writer.write_dlis_file(dlis_file_name=dlis_file_name)

