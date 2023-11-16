import numpy as np
import h5py
from typing import Union
import os
from configparser import ConfigParser


def load_hdf5(data_file_name: Union[str, bytes, os.PathLike], key: str = 'contents') -> np.ndarray:
    """Load HDF5 data into a structured numpy array.

    Args:
        data_file_name: Name of the HDF5 file.
        key:            Top-level group name in the file.

    Note:
        This method assumes a rather simple structure of the HDF5 file: a single relevant top-level group
        containing only simple datasets (not subgroups).
        All datasets found under the top-level header ('key') are loaded.

    Returns:
        A structured numpy array; see `docs <https://numpy.org/doc/stable/user/basics.rec.html>`_

    Raises:
        RuntimeError:
            - if datasets with mismatching lengths are found in the HDF5 file,
            - if a dataset with more than 2 dimensions is found.
    """

    # open the HDF5 file and access the data found under the top-level group name
    h5_data = h5py.File(data_file_name, 'r')[f'/{key}/']

    dtype = []  #: structured data types for the data sets; set names, element types, and optionally sizes (row lengths)
    arrays = []  #: data sets to be combined into the structured array
    n_rows = None  #: total number of rows ('samples') in each data set and in the final structured array (tbd.)

    for key in h5_data.keys():
        key_data = h5_data.get(key)[:]
        arrays.append(key_data)

        # determine the dtype of the data set (2- or 3-tuple)
        dt = (key, key_data.dtype)
        if key_data.ndim > 1:
            if key_data.ndim > 2:
                raise RuntimeError("Data sets with more than 2 dimensions are not supported")
            dt = (*dt, key_data.shape[-1])  # 3-tuple if the data set has multiple samples per row
        dtype.append(dt)

        # determine (first iteration) or check (next iterations) the number of rows - needs to be consistent
        if n_rows is None:
            n_rows = key_data.shape[0]
        else:
            if n_rows != key_data.shape[0]:
                raise RuntimeError(
                    "Datasets in the file have different lengths; the data cannot be transformed to DLIS format")

    # combine the arrays into a structured numpy array
    full_data = np.zeros(n_rows, dtype=dtype)  # preallocate the array with the now-known number of rows and dtype
    for key, arr in zip(h5_data.keys(), arrays):
        full_data[key] = arr  # structured numpy arrays support accessing data sets by their names (a bit like dicts)

    return full_data


def load_config(fname):
    cfg = ConfigParser()
    cfg.read(fname)
    return cfg
