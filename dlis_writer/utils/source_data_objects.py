import numpy as np
import h5py
from typing import Union, Optional
import os
from typing_extensions import Self
import logging
from configparser import ConfigParser

from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.converters import ReprCodeConverter


logger = logging.getLogger(__name__)


data_source_type = Union[h5py.File, np.ndarray, dict[str, np.ndarray]]


class SourceDataObject:
    """Keep reference to source data. Produce chunks of input data as asked, in the form of a structured numpy array."""

    def __init__(self, data_source: data_source_type, mapping: dict[str, str],
                 known_dtypes: Optional[dict[str, np.dtype]] = None, **kwargs):
        """Initialise a SourceDataObject.

        Args:
            data_source     :   Original data object.
            mapping         :   Mapping of data type names on the names of data in the data source (e.g. on the paths to
                                particular HDF5 datasets).
            known_dtypes    :   Mapping of data type names on data types (if any are known). Does not have to contain
                                all dtypes. Can also be completely omitted. Missing data types are determined from
                                the data.
            **kwargs        :   The slot for additional keyword arguments has been added for signature consistency
                                with all subclasses. No other keyword arguments should actually be passed.

            Note:
                All data sets from 'mapping' should be found in the 'data_source'. On the other hand, 'data_source'
                can contain more data sets than mentioned in 'mapping' and the order does not have to match.
                Only the data sets found in 'mapping', with that exact order, will be included in the produced
                data chunks, passed to the DLIS file writer loop.
                All datasets (of the ones mentioned in 'mapping') are required to have the same length.
        """

        if kwargs:
            raise ValueError(f"Unexpected keyword arguments passed to initialisation of SourceDataObject: {kwargs}")

        self._data_source = data_source
        self._mapping = mapping

        # numpy dtype object which will be used for constructing data chunks (see 'load_chunk')
        self._dtype = self.determine_dtypes(self._data_source, self._mapping, known_dtypes=known_dtypes)

        # total number of rows - guessed from the first dataset
        self._n_rows = self._data_source[next(iter(mapping.values()))].shape[0]

    @property
    def n_rows(self) -> int:
        """Total number of data rows."""

        return self._n_rows

    @property
    def data_source(self) -> data_source_type:
        """Source data object."""

        return self._data_source

    @property
    def dtype(self) -> np.dtype:
        """Data type of the structured numpy arrays, in the form of which the input data chunks are loaded."""

        return self._dtype

    @staticmethod
    def determine_dtypes(data_object: data_source_type, mapping: dict[str, str],
                         known_dtypes: Optional[dict[str, np.dtype]] = None) -> np.dtype:
        """Determine the structured numpy dtype for the provided data, with given data names mapping.

        Args:
            data_object     :   Original data object.
            mapping         :   Mapping of data type names on the names of data in the data source (e.g. on the paths to
                                particular HDF5 datasets).
            known_dtypes    :   Mapping of data type names on data types (if any are known). Does not have to contain
                                all dtypes. Can also be completely omitted. Missing data types are determined from
                                the data.

        Returns:
            A numpy.dtype object, specifying the names, dtypes, and (if not 1D) shapes of the data sets to be contained
            in the loaded input data chunks.
        """

        dtypes = []  # list of data type tuples, later transformed to a np.dtype
        known_dtypes = known_dtypes or {}

        for dtype_name, dataset_name in mapping.items():
            try:
                dset = data_object[dataset_name]
            except (ValueError, KeyError):
                raise ValueError(f"No dataset '{dataset_name}' found in the source data")
            dset_row0 = dset[0:1]  # get in form of a 1-element (or 1-row) array, not a single number
            # for h5 data, the above retrieves the first row of the current data set

            # determine the dtype of the data set (2- or 3-tuple)
            dt = (dtype_name, known_dtypes.get(dtype_name, dset_row0.dtype))
            if dset_row0.ndim > 1:
                if dset_row0.ndim > 2:
                    raise RuntimeError("Data sets with more than 2 dimensions are not supported")
                dt = (*dt, dset_row0.shape[-1])  # 3-tuple if the data set has multiple samples per row - add the width
            dtypes.append(dt)

        return np.dtype(dtypes)

    def __getitem__(self, item: str) -> Union[np.ndarray, h5py.Dataset]:
        """Retrieve a dataset of the given name from the dataset.

        The name should be the one used for the dtype name, not the data set name/location
        (i.e. taken from the keys, not values, of the 'mapping' dictionary specified at init).

        Returns:
            h5py.Dataset if the source data object was a h5py.File; np.ndarray otherwise.
        """

        try:
            data = self._data_source[self._mapping[item]]
        except (ValueError, KeyError):
            raise ValueError(f"No dataset '{item}' found in the source data")
        return data

    def load_chunk(self, start: int, stop: Union[int, None]) -> np.ndarray:
        """Copy a chunk of the source data into a structured numpy array of the pre-determined dtype.

        The returned chunk is a horizontal slice of the source data, possibly reshaped to match the desired format
        (i.e. the order and names of data sets). All data sets specified in the initial mapping are included.
        The range of the included rows of data is determined by the 'start' and 'stop' arguments.

        Args:
            start   :   Start index.
            stop    :   Stop index. If None, all data from start index till the end will be loaded.

        Returns:
            A structured numpy array, containing the required chunks of all the relevant data sets from the source data.
        """

        idx = slice(start, stop)
        n_rows = (stop or self._n_rows) - start

        chunk = np.zeros(n_rows, dtype=self._dtype)
        for key, loc in self._mapping.items():
            chunk[key] = self._data_source[loc][idx]

        return chunk

    def make_chunked_generator(self, chunk_rows: Union[int, None]):
        """Define a generator yielding consecutive chunks of input data with the specified size.

        Args:
            chunk_rows  :   Maximal number of rows per chunk (the last chunk might be smaller, depending on the total
                            size of the data). If None, the entire data is loaded as a single chunk.

        Yields:
            Structured numpy.ndarray objects with the consecutive chunks of the source data.
        """

        if chunk_rows is None:
            chunk_rows = self._n_rows
            n_full_chunks = 1
            remainder_rows = 0
            logger.debug(f"Data will be loaded in a single chunk of {self._n_rows}")
        else:
            n_full_chunks, remainder_rows = divmod(self._n_rows, chunk_rows)
            if n_full_chunks:
                rem = f" plus a last, smaller chunk of {remainder_rows} rows" if remainder_rows else ""
                logger.debug(f"Data will be loaded in {n_full_chunks} chunk(s) of {chunk_rows} rows" + rem)
            else:
                logger.debug(f"Provided chunk size ({chunk_rows}) is larger than the total size of the data "
                             f"({self._n_rows}); data will be loaded in a single chunk of {remainder_rows}")

        total_chunks = n_full_chunks + int(bool(remainder_rows))

        for i in range(n_full_chunks):
            logger.debug(f"Loading chunk {i+1}/{total_chunks} ({chunk_rows} rows)")
            yield from self.load_chunk(i * chunk_rows, (i + 1) * chunk_rows)

        if remainder_rows:
            logger.debug(f"Loading chunk {total_chunks}/{total_chunks} ({remainder_rows} rows)")
            yield from self.load_chunk(n_full_chunks * chunk_rows, None)

    @staticmethod
    def make_mappings_from_config(config: ConfigParser) -> tuple[dict[str, str], dict[str, np.dtype]]:
        """Create data set name mapping and dtype mapping (where possible) from a config object.

        Args:
            config  :   Config object containing the information on the data sets under 'Channel-...' headings
                        (only those which are added to Frame section in the config as 'channels' or 'channels.value').

        Returns:
            name mapping    :   a dictionary mapping data type names (names of the channels) on the names/locations
                                of the corresponding datasets (e.g. HFD5 data set paths).
            dtype mapping   :   a dictionary mapping data type names on known data types, inferred from representation
                                codes specified for the corresponding channels (if available).

        Note:
            The name mapping dict will contain all data sets which will later be included in the loaded chunks.
            The dtype mapping dict will contain only the known data types (where a representation code was specified).
        """

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

                # add channel info to the name mapping
                if 'dataset_name' in cs.keys():
                    name_mapping[cs['name']] = cs['dataset_name']
                else:
                    name_mapping[cs['name']] = cs['name']

                # add channel info to the dtype mapping
                repr_code = cs.get('representation_code', cs.get('representation_code.value', None))
                if isinstance(repr_code, str) and repr_code.isdigit():
                    repr_code = RepresentationCode(int(repr_code))
                elif repr_code is not None:
                    repr_code = RepresentationCode[repr_code]

                if repr_code is not None:
                    dtype_mapping[cs['name']] = SourceDataObject.get_dtype(repr_code)

        return name_mapping, dtype_mapping

    @staticmethod
    def get_dtype(repr_code: Union[RepresentationCode, None], allow_none: bool = True) -> np.dtype:
        """Determine a numpy dtype for a given representation code.

        Args:
            repr_code   :   Representation code to convert to a numpy dtype.
            allow_none  :   If True and 'repr_code' is None, return the default repr code - FDOUBL.

        Returns:
            A numpy.dtype object corresponding to the given representation code.
        """

        if allow_none and repr_code is None:
            return SourceDataObject.get_dtype(RepresentationCode.FDOUBL)

        return ReprCodeConverter.repr_codes_to_numpy_dtypes.get(repr_code)

    @classmethod
    def from_config(cls, data_source: data_source_type, config: ConfigParser, **kwargs) -> Self:
        """Create a SourceDataObject from the source data object and config info."""

        name_mapping, dtype_mapping = cls.make_mappings_from_config(config)
        return cls(data_source, name_mapping, known_dtypes=dtype_mapping, **kwargs)


class HDF5Interface(SourceDataObject):
    """Wrap source data provided in the form of a HDF5 file."""

    def __init__(self, data_file_name: Union[str, bytes, os.PathLike], mapping: dict, **kwargs):
        """Initialise HDF5Interface.

        Args:
            data_file_name  :   Name of/path to the HDF5 file containing the source data.
            mapping         :   Mapping of the names of data sets (data types) to be included on the corresponding
                                data set paths in the file.
            **kwargs        :   Additional keyword arguments passed to __init__ of SourceDataObject.
        """

        # open the file
        h5_data = h5py.File(data_file_name, 'r')

        # add a forward slash at the beginning of each value in the mapping dict - if missing
        mapping = {k: (f'/{v}' if not v.startswith('/') else v) for k, v in mapping.items()}

        super().__init__(h5_data, mapping, **kwargs)

    def close(self):
        """Close the HDF5 file (if open)."""

        if hasattr(self, '_data_source'):  # object might be partially initialised
            try:
                self._data_source.close()
            except TypeError as exc:
                logger.error(f"Error closing the source data file: {exc}")
            else:
                logger.debug("Source data file closed")

    def __del__(self):
        """Close the HDF5 file when deleting the object (if still open at this point)."""

        self.close()


class NumpyInterface(SourceDataObject):
    """Wrap source data provided in the form of a structured numpy array."""

    def __init__(self, arr: np.ndarray, mapping: Optional[dict] = None, **kwargs):
        """Initialise NumpyInterface.

        Args:
            arr         :   Source data - structured numpy array.
            mapping     :   Mapping of target data type names on the data type names found in the source array.
                            Optional; if not provided, it is assumed that the target data types (data sets)
                            are the same as the source ones.
            **kwargs    :   Additional keyword arguments passed to __init__ of SourceDataObject.
        """

        self._check_source_arr(arr)

        if not mapping:
            # default mapping: 1 to 1 for all existing data type names
            mapping = {k: k for k in arr.dtype.names}

        super().__init__(arr, mapping, **kwargs)

    def load_chunk(self, start: int, stop: Union[int, None]) -> np.ndarray:
        """Load a chunk of the input data.

        If the target data type (data sets names and dtypes) is the same as the one in the source array,
        take a slice of the source array directly.
        Otherwise, use the 'load_chunk' from the superclass to copy the relevant data sets into a new structured array.

        Args:
            start   :   Start index.
            stop    :   Stop index. If None, all data from start index till the end will be loaded.

        Returns:
            A structured numpy array, containing the required chunks of all the relevant data sets from the source data.
        """

        if self._dtype == self._data_source.dtype:
            return self._data_source[start:stop]

        return super().load_chunk(start, stop)

    @staticmethod
    def _check_source_arr(arr: np.ndarray):
        """Check that the input array is a structured, 1D numpy array."""

        if not isinstance(arr, np.ndarray):
            raise TypeError(f"Expected a numpy.ndarray; got {type(arr)}")

        if arr.ndim > 1:
            raise ValueError("Source array must be 1-dimensional")

        if not arr.dtype.names:
            raise ValueError("Input must be a structured numpy array")


class DictInterface(SourceDataObject):
    """Wrap source data provided in the form of a dictionary of numpy arrays."""

    def __init__(self, data_dict: dict[str, np.ndarray], mapping: dict = None, **kwargs):
        """Initialise DictInterface.

        Args:
            data_dict   :   Source data - dict of numpy arrays.
            mapping     :   Mapping of target data type names on the keys found in the data dictionary.
                            Optional; if not provided, it is assumed that all items of the data dict should be included
                            in the target structured arrays.
            **kwargs    :   Additional keyword arguments passed to __init__ of SourceDataObject.
        """

        self._check_source_dict(data_dict)

        if not mapping:
            # default mapping: 1 to 1 for all keys of the data dict
            mapping = {k: k for k in data_dict.keys()}

        super().__init__(data_dict, mapping, **kwargs)

    @staticmethod
    def _check_source_dict(data_dict: dict[str, np.ndarray]):
        """Check that all values of the source dictionary are numpy arrays."""

        if not all(isinstance(v, np.ndarray) for v in data_dict.values()):
            raise ValueError(f"Dict values must be numpy arrays; "
                             f"got {', '.join(str(type(v)) for v in data_dict.values())}")
