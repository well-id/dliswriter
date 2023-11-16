import numpy as np
import h5py
from typing import Union
import os


class SourceDataObject:
    def __init__(self, data_source, mapping):
        self._data_source = data_source
        self._mapping = mapping

        self._dtype = self.determine_dtypes(self._data_source, self._mapping)

        self._n_rows = self._data_source[next(iter(mapping.values()))].shape[0]

    @staticmethod
    def determine_dtypes(data_object, mapping: dict):
        dtypes = []
        for dtype_name, dataset_name in mapping.items():
            try:
                dset = data_object[dataset_name]
            except (ValueError, KeyError):
                raise ValueError(f"No dataset '{dataset_name}' found in the source data")
            dset_row0 = dset[0:1]  # get in form of a 1-element array, not a single number

            # determine the dtype of the data set (2- or 3-tuple)
            dt = (dtype_name, dset_row0.dtype)
            if dset_row0.ndim > 1:
                if dset_row0.ndim > 2:
                    raise RuntimeError("Data sets with more than 2 dimensions are not supported")
                dt = (*dt, dset_row0.shape[-1])  # 3-tuple if the data set has multiple samples per row
            dtypes.append(dt)

        return np.dtype(dtypes)

    def load_chunk(self, start: int, stop: Union[int, None]):
        idx = slice(start, stop)
        n_rows = (stop or self._n_rows) - start

        chunk = np.zeros(n_rows, dtype=self._dtype)
        for key, loc in self._mapping.items():
            chunk[key] = self._data_source[loc][idx]

        return chunk

    def make_chunked_generator(self, chunk_rows):
        if chunk_rows is None:
            n_full_chunks = 1
            remainder_rows = 0
        else:
            n_full_chunks, remainder_rows = divmod(self._n_rows, chunk_rows)

        for i in range(n_full_chunks):
            yield from self.load_chunk(i * chunk_rows, (i + 1) * chunk_rows)

        if remainder_rows:
            yield from self.load_chunk(n_full_chunks * chunk_rows, None)


class HDF5Interface(SourceDataObject):
    def __init__(self, data_file_name: Union[str, bytes, os.PathLike], mapping: dict, **kwargs):

        # open the HDF5 file and access the data found under the top-level group name
        h5_data = h5py.File(data_file_name, 'r', **kwargs)

        mapping = {k: (f'/{v}' if not v.startswith('/') else v) for k, v in mapping.items()}

        super().__init__(h5_data, mapping)

    def close(self):
        self._data_source.close()

    def __del__(self):
        self.close()


class NumpyInterface(SourceDataObject):
    def __init__(self, arr: np.array, mapping: dict = None):
        if not arr.dtype.names:
            raise ValueError("Input must be a structured numpy array")

        if not mapping:
            mapping = {k: k for k in arr.dtype.names}

        super().__init__(arr, mapping)

    def load_chunk(self, start: int, stop: Union[int, None]):
        if self._dtype == self._data_source.dtype:
            return self._data_source[start:stop]

        return super().load_chunk(start, stop)


class DictInterface(SourceDataObject):
    def __init__(self, data_dict, mapping: dict = None):
        if not all(isinstance(v, np.ndarray) for v in data_dict.values()):
            raise ValueError(f"Dict values must be numpy arrays; "
                             f"got {', '.join(str(type(v)) for v in data_dict.values)}")

        if not mapping:
            mapping = {k: k for k in data_dict.keys()}

        super().__init__(data_dict, mapping)
