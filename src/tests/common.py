import numpy as np
from contextlib import contextmanager
from dlisio import dlis    # type: ignore  # untyped library
from pathlib import Path
import h5py    # type: ignore  # untyped library
from typing import Union
import os
from configparser import ConfigParser

from dlis_writer.writer.write_dlis_file import write_dlis_file
from dlis_writer.utils.source_data_wrappers import NumpyDataWrapper, HDF5DataWrapper, SourceDataWrapper
from dlis_writer.logical_record.eflr_types import eflr_sets


def clear_eflr_instance_registers():
    """Remove all defined instances of EFLR from the internal dicts. Clear the EFLRObject dicts of the instances."""

    for eflr_type in eflr_sets:
        for eflr in eflr_type.get_all_sets():
            eflr.clear_eflr_item_dict()
        eflr_type.clear_set_instance_dict()


N_COLS = 128


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

