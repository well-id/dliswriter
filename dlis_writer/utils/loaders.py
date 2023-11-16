import numpy as np
import h5py
from typing import Union
import os
from configparser import ConfigParser


class HDF5Interface:
    def __init__(self, data_file_name: Union[str, bytes, os.PathLike], mapping: dict, **kwargs):
        # open the HDF5 file and access the data found under the top-level group name
        self._h5_data = h5py.File(data_file_name, 'r', **kwargs)
        self._mapping = {k: (f'/{v}' if not v.startswith('/') else v) for k, v in mapping.items()}

        self._dtype = self.determine_dtypes(self._h5_data, self._mapping)

        self._n_rows = self._h5_data.get(next(iter(self._mapping.values()))).shape[0]

    @staticmethod
    def determine_dtypes(h5_data: h5py.File, mapping: dict):
        dtypes = []
        for key, loc in mapping.items():
            dset = h5_data.get(loc)
            if not dset:
                raise ValueError(f"No dataset '{loc}' found in the file")
            key_data = h5_data.get(loc)[0:1]  # get in form of a 1-element array, not a single number

            # determine the dtype of the data set (2- or 3-tuple)
            dt = (key, key_data.dtype)
            if key_data.ndim > 1:
                if key_data.ndim > 2:
                    raise RuntimeError("Data sets with more than 2 dimensions are not supported")
                dt = (*dt, key_data.shape[-1])  # 3-tuple if the data set has multiple samples per row
            dtypes.append(dt)

        return np.dtype(dtypes)

    def load_chunk(self, start: int, stop: Union[int, None]):
        idx = slice(start, stop)
        n_rows = (stop or self._n_rows) - start

        chunk = np.zeros(n_rows, dtype=self._dtype)
        for key, loc in self._mapping.items():
            chunk[key] = self._h5_data.get(loc)[idx]

        return chunk

    def close(self):
        self._h5_data.close()

    def __del__(self):
        self.close()

    def make_chunked_generator(self, chunk_rows):
        n_full_chunks, remainder_rows = divmod(self._n_rows, chunk_rows)

        for i in range(n_full_chunks):
            yield from self.load_chunk(i * chunk_rows, (i + 1) * chunk_rows)

        if remainder_rows:
            yield from self.load_chunk(n_full_chunks * chunk_rows, None)


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
