import numpy as np
import pytest
from contextlib import contextmanager
from dlisio import dlis    # type: ignore  # untyped library
from pathlib import Path
import h5py    # type: ignore  # untyped library
from typing import Union
import os
from configparser import ConfigParser

from dlis_writer.writer.write_dlis_file import write_dlis_file
from dlis_writer.utils.source_data_wrappers import NumpyDataWrapper, HDF5DataWrapper, SourceDataWrapper

from tests.common import clear_eflr_instance_registers


N_COLS = 128


@pytest.fixture(scope='session')
def reference_data_path(base_data_path: Path) -> Path:
    """Path to the reference HDF5 data file."""

    return base_data_path / 'resources/mock_data.hdf5'


@pytest.fixture(scope='session')
def reference_data(reference_data_path: Path):
    """The reference HDF5 data file, open in read mode."""

    f = h5py.File(reference_data_path, 'r')
    yield f
    f.close()


@pytest.fixture(scope='session')
def short_reference_data_path(base_data_path: Path) -> Path:
    """Path to the HDF5 file with short version of the reference data."""

    return base_data_path / 'resources/mock_data_short.hdf5'


@pytest.fixture(scope='session')
def short_reference_data(short_reference_data_path: Path):
    """The reference short HDF5 data file, open in read mode."""

    f = h5py.File(short_reference_data_path, 'r')
    yield f
    f.close()


@contextmanager
def load_dlis(fname: Union[str, bytes, os.PathLike]):
    """Load a DLIS file using dlisio. Yield the open file. Close the file on return to the context."""

    with dlis.load(fname) as (f, *tail):
        try:
            yield f
        finally:
            pass


def select_channel(f: dlis.file.LogicalFile, name: str) -> dlis.channel.Channel:
    """Search for a channel with given name in the dlis file and return it."""

    return f.object("CHANNEL", name)


def write_file(data: Union[np.ndarray, str, Path, SourceDataWrapper], dlis_file_name: Union[str, Path],
               config: ConfigParser):
    """Load / adapt the provided data and write a DLIS file using the provided config information."""

    clear_eflr_instance_registers()

    if isinstance(data, np.ndarray):
        data = NumpyDataWrapper.from_config(data, config)
    elif isinstance(data, (str, Path)):
        data = HDF5DataWrapper.from_config(data, config)
    elif not isinstance(data, SourceDataWrapper):
        raise TypeError(f"Expected a SourceDataObject, numpy.ndarray, or a path to a HDF5 file; got {type(data)}")

    write_dlis_file(data=data, config=config, dlis_file_name=dlis_file_name)

