import numpy as np
import h5py
from typing import Union
import os
import logging
from configparser import ConfigParser

from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.converters import ReprCodeConverter



logger = logging.getLogger(__name__)


class SourceDataObject:
    def __init__(self, data_source, mapping, known_dtypes: dict = None, **kwargs):
        if kwargs:
            raise ValueError(f"Unexpected keyword arguments passed to initialisation of SourceDataObject: {kwargs}")
        self._data_source = data_source
        self._mapping = mapping

        self._dtype = self.determine_dtypes(self._data_source, self._mapping, known_dtypes=known_dtypes)

        self._n_rows = self._data_source[next(iter(mapping.values()))].shape[0]

    @property
    def n_rows(self):
        return self._n_rows

    @property
    def dtype(self):
        return self._dtype

    @staticmethod
    def determine_dtypes(data_object, mapping: dict, known_dtypes: dict = None):
        dtypes = []
        for dtype_name, dataset_name in mapping.items():
            try:
                dset = data_object[dataset_name]
            except (ValueError, KeyError):
                raise ValueError(f"No dataset '{dataset_name}' found in the source data")
            dset_row0 = dset[0:1]  # get in form of a 1-element array, not a single number

            # determine the dtype of the data set (2- or 3-tuple)
            dt = (dtype_name, known_dtypes.get(dtype_name, dset_row0.dtype))
            if dset_row0.ndim > 1:
                if dset_row0.ndim > 2:
                    raise RuntimeError("Data sets with more than 2 dimensions are not supported")
                dt = (*dt, dset_row0.shape[-1])  # 3-tuple if the data set has multiple samples per row
            dtypes.append(dt)

        return np.dtype(dtypes)

    def __getitem__(self, item):
        try:
            data = self._data_source[self._mapping[item]]
        except (ValueError, KeyError):
            raise ValueError(f"No dataset '{item}' found in the source data")
        return data

    def load_chunk(self, start: int, stop: Union[int, None]):
        idx = slice(start, stop)
        n_rows = (stop or self._n_rows) - start

        chunk = np.zeros(n_rows, dtype=self._dtype)
        for key, loc in self._mapping.items():
            chunk[key] = self._data_source[loc][idx]

        return chunk

    def make_chunked_generator(self, chunk_rows):
        if chunk_rows is None:
            chunk_rows = self._n_rows
            n_full_chunks = 1
            remainder_rows = 0
            logger.debug("Data will be loaded in a single chunk")
        else:
            n_full_chunks, remainder_rows = divmod(self._n_rows, chunk_rows)
            rem = f" plus a last, smaller chunk of {remainder_rows} rows" if remainder_rows else ""
            logger.debug(f"Data will be loaded in {n_full_chunks} chunks of {chunk_rows} rows" + rem)

        total_chunks = n_full_chunks + int(bool(remainder_rows))

        for i in range(n_full_chunks):
            logger.debug(f"Loading chunk {i+1}/{total_chunks} ({chunk_rows} rows)")
            yield from self.load_chunk(i * chunk_rows, (i + 1) * chunk_rows)

        if remainder_rows:
            logger.debug(f"Loading chunk {total_chunks}/{total_chunks} ({remainder_rows} rows)")
            yield from self.load_chunk(n_full_chunks * chunk_rows, None)

    @staticmethod
    def make_mappings_from_config(config: ConfigParser):
        name_mapping = {}
        dtype_mapping = {}

        frame_config = config['Frame']
        if 'channels' in frame_config:
            frame_channels = frame_config['channels']
        elif 'channels.value' in frame_config:
            frame_channels = frame_config['channels.value']
        else:
            raise RuntimeError("No channels defined for the frame")
        frame_channels = frame_channels.split(', ')

        for section in config.sections():
            if section.startswith('Channel') and section in frame_channels:
                cs = config[section]
                if 'dataset_name' in cs.keys():
                    name_mapping[cs['name']] = cs['dataset_name']
                else:
                    name_mapping[cs['name']] = cs['name']

                repr_code = cs.get('representation_code', cs.get('representation_code.value', None))
                if isinstance(repr_code, str) and repr_code.isdigit():
                    repr_code = RepresentationCode(int(repr_code))
                elif repr_code is not None:
                    repr_code = RepresentationCode[repr_code]

                dtype_mapping[cs['name']] = SourceDataObject.get_dtype(repr_code)

        return name_mapping, dtype_mapping

    @staticmethod
    def get_dtype(repr_code: RepresentationCode):
        if repr_code is None:
            return SourceDataObject.get_dtype(RepresentationCode.FDOUBL)

        return ReprCodeConverter.repr_codes_to_numpy_dtypes.get(repr_code)

    @classmethod
    def from_config(cls, data_source, config, **kwargs):
        name_mapping, dtype_mapping = cls.make_mappings_from_config(config)
        return cls(data_source, name_mapping, known_dtypes=dtype_mapping, **kwargs)


class HDF5Interface(SourceDataObject):
    def __init__(self, data_file_name: Union[str, bytes, os.PathLike], mapping: dict, **kwargs):

        # open the HDF5 file and access the data found under the top-level group name
        h5_data = h5py.File(data_file_name, 'r')

        mapping = {k: (f'/{v}' if not v.startswith('/') else v) for k, v in mapping.items()}

        super().__init__(h5_data, mapping, **kwargs)

    def close(self):
        if hasattr(self, '_data_source'):  # object might be partially initialised
            try:
                self._data_source.close()
            except TypeError as exc:
                logger.error(f"Error closing the source data file: {exc}")
            else:
                logger.debug("Source data file closed")

    def __del__(self):
        self.close()


class NumpyInterface(SourceDataObject):
    def __init__(self, arr: np.array, mapping: dict = None, **kwargs):
        if not arr.dtype.names:
            raise ValueError("Input must be a structured numpy array")

        if not mapping:
            mapping = {k: k for k in arr.dtype.names}

        super().__init__(arr, mapping, **kwargs)

    def load_chunk(self, start: int, stop: Union[int, None]):
        if self._dtype == self._data_source.dtype:
            return self._data_source[start:stop]

        return super().load_chunk(start, stop)


class DictInterface(SourceDataObject):
    def __init__(self, data_dict, mapping: dict = None, **kwargs):
        if not all(isinstance(v, np.ndarray) for v in data_dict.values()):
            raise ValueError(f"Dict values must be numpy arrays; "
                             f"got {', '.join(str(type(v)) for v in data_dict.values)}")

        if not mapping:
            mapping = {k: k for k in data_dict.keys()}

        super().__init__(data_dict, mapping, **kwargs)
