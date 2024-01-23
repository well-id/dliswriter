import numpy as np
import h5py    # type: ignore  # untyped library
from typing import Union, Optional, Any, Generator
import logging
from abc import ABC

from dlis_writer.utils.converters import ReprCodeConverter
from dlis_writer.utils.types import data_form_type, data_source_type, file_name_type, numpy_dtype_type


logger = logging.getLogger(__name__)


class SourceDataWrapper(ABC):
    """Keep reference to source data. Produce chunks of input data as asked, in the form of a structured numpy array."""

    def __init__(self, data_source: data_source_type, mapping: dict[str, str],
                 known_dtypes: Optional[dict[str, numpy_dtype_type]] = None, from_idx: int = 0,
                 to_idx: Optional[int] = None) -> None:
        """Initialise a SourceDataWrapper.

        Args:
            data_source     :   Original data object.
            mapping         :   Mapping of data type names on the names of data in the data source (e.g. on the paths to
                                particular HDF5 datasets).
            known_dtypes    :   Mapping of data type names on data types (if any are known). Does not have to contain
                                all dtypes. Can also be completely omitted. Missing data types are determined from
                                the data.
            from_idx        :   Index from which data should be loaded (or number of initial rows to ignore).
            to_idx          :   Index up to which data should be loaded.

            Note:
                All data sets from 'mapping' should be found in the 'data_source'. On the other hand, 'data_source'
                can contain more data sets than mentioned in 'mapping' and the order does not have to match.
                Only the data sets found in 'mapping', with that exact order, will be included in the produced
                data chunks, passed to the DLIS file writer loop.
                All datasets (of the ones mentioned in 'mapping') are required to have the same length.
        """

        self._data_source = data_source
        self._mapping = mapping

        # numpy dtype object which will be used for constructing data chunks (see 'load_chunk')
        self._dtype = self.determine_dtypes(self._data_source, self._mapping, known_dtypes=known_dtypes)

        # total number of rows - guessed from the first dataset
        total_n_rows = self._data_source[next(iter(mapping.values()))].shape[0]

        self._from_idx = from_idx
        self._to_idx = to_idx if to_idx is not None else total_n_rows
        self._n_rows = self._to_idx - self._from_idx  # number of rows to be loaded

        if self._from_idx >= total_n_rows:
            raise ValueError(f"Starting index {self._from_idx} too large for total n. rows {total_n_rows}")
        if self._n_rows < 1:
            raise ValueError(f"Starting index {self._from_idx} and end index {self._to_idx} do not yield a positive "
                             f"number of rows to be loaded")

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
                         known_dtypes: Optional[dict[str, numpy_dtype_type]] = None) -> np.dtype:
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
            dt: Union[tuple[str, Any], tuple[str, Any, int]]

            try:
                dset = data_object[dataset_name]
            except (ValueError, KeyError):
                raise ValueError(f"No dataset '{dataset_name}' found in the source data")
            dset_row0 = dset[0:1]  # get in form of a 1-element (or 1-row) array, not a single number
            # for h5 data, the above retrieves the first row of the current data set

            # determine the numpy number dtype
            number_type = known_dtypes.get(dtype_name, dset_row0.dtype)
            ReprCodeConverter.validate_numpy_dtype(number_type)

            # determine the dtype of the data set (2- or 3-tuple)
            dt = (dtype_name, number_type)
            if dset_row0.ndim > 1:
                if dset_row0.ndim > 2:
                    raise RuntimeError("Data sets with more than 2 dimensions are not supported")
                dt = (*dt, dset_row0.shape[-1])  # 3-tuple if the data set has multiple samples per row - add the width
            dtypes.append(dt)

        return np.dtype(dtypes)

    def __getitem__(self, item: str) -> np.ndarray:
        """Retrieve a dataset of the given name from the dataset.

        The name should be the one used for the dtype name, not the data set name/location
        (i.e. taken from the keys, not values, of the 'mapping' dictionary specified at init).

        Returns:
            A np.ndarray with the data.
        """

        try:
            data = self._data_source[self._mapping[item]]
        except (ValueError, KeyError):
            raise ValueError(f"No dataset '{item}' found in the source data")
        return data[self._from_idx:self._to_idx]

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

        if start < 0:
            raise ValueError("Start row cannot be negative")

        if start > self._n_rows:
            raise ValueError(f"Cannot load chunk from row {start} because the data source has only {self._n_rows} rows")

        if stop is None:
            stop = self._n_rows

        if stop > self._n_rows:
            raise ValueError(f"Cannot load chunk up to row {stop} because the data source has only {self._n_rows} rows")
        if stop < start:
            raise ValueError(f"Stop row cannot be smaller than start row; got {stop} and {start}")

        idx = slice(self._from_idx + start, self._from_idx + stop)
        n_rows = stop - start

        chunk = np.zeros(n_rows, dtype=self._dtype)
        for key, loc in self._mapping.items():
            chunk[key] = self._data_source[loc][idx]

        return chunk

    def make_chunked_generator(self, chunk_rows: Union[int, None]) -> Generator:
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

    @classmethod
    def make_wrapper(cls, source: data_form_type, mapping: Optional[dict] = None,
                     **kwargs: Any) -> Union["DictDataWrapper", "NumpyDataWrapper", "HDF5DataWrapper"]:

        if isinstance(source, dict):
            return DictDataWrapper(source, mapping, **kwargs)

        if isinstance(source, np.ndarray):
            return NumpyDataWrapper(source, mapping, **kwargs)

        try:
            source_str = str(source)
        except (TypeError, ValueError):
            raise TypeError(f"Expected a path-like; got {type(source)}: {source}")
        if source_str.split('.')[-1].lower() not in ('h5', 'hdf5'):
            raise ValueError(f"Expected a path to an HDF5 file; got {source_str}")
        if mapping is None:
            raise ValueError("Mapping must be provided to create a HDF5DataWrapper")
        return HDF5DataWrapper(source, mapping, **kwargs)


class HDF5DataWrapper(SourceDataWrapper):
    """Wrap source data provided in the form of a HDF5 file."""

    _data_source: h5py.File

    def __init__(self, data_file_name: file_name_type, mapping: dict,
                 known_dtypes: Optional[dict[str, numpy_dtype_type]] = None, from_idx: int = 0,
                 to_idx: Optional[int] = None) -> None:
        """Initialise HDF5DataWrapper.

        Args:
            data_file_name  :   Name of/path to the HDF5 file containing the source data.
            mapping         :   Mapping of the names of data sets (data types) to be included on the corresponding
                                data set paths in the file.
            known_dtypes    :   Mapping of data type names on data types (if any are known). Does not have to contain
                                all dtypes. Can also be completely omitted. Missing data types are determined from
                                the data.
            from_idx        :   Index from which data should be loaded (or number of initial rows to ignore).
            to_idx          :   Index up to which data should be loaded.
        """

        # open the file
        h5_data = h5py.File(data_file_name, 'r')

        # add a forward slash at the beginning of each value in the mapping dict - if missing
        mapping = {k: (f'/{v}' if not v.startswith('/') else v) for k, v in mapping.items()}

        super().__init__(h5_data, mapping, known_dtypes=known_dtypes, from_idx=from_idx, to_idx=to_idx)

    def close(self) -> None:
        """Close the HDF5 file (if open)."""

        if hasattr(self, '_data_source'):  # object might be partially initialised
            try:
                self._data_source.close()
            except TypeError as exc:
                logger.error(f"Error closing the source data file: {exc}")
            else:
                logger.debug("Source data file closed")

    def __del__(self) -> None:
        """Close the HDF5 file when deleting the object (if still open at this point)."""

        self.close()


class NumpyDataWrapper(SourceDataWrapper):
    """Wrap source data provided in the form of a structured numpy array."""

    _data_source: np.ndarray

    def __init__(self, arr: np.ndarray, mapping: Optional[dict] = None,
                 known_dtypes: Optional[dict[str, numpy_dtype_type]] = None, from_idx: int = 0,
                 to_idx: Optional[int] = None) -> None:
        """Initialise NumpyDataWrapper.

        Args:
            arr             :   Source data - structured numpy array.
            mapping         :   Mapping of target data type names on the data type names found in the source array.
                                Optional; if not provided, it is assumed that the target data types (data sets)
                                are the same as the source ones.
            known_dtypes    :   Mapping of data type names on data types (if any are known). Does not have to contain
                                all dtypes. Can also be completely omitted. Missing data types are determined from
                                the data.
            from_idx        :   Index from which data should be loaded (or number of initial rows to ignore).
            to_idx          :   Index up to which data should be loaded.

        """

        self._check_source_arr(arr)

        if not mapping:
            # default mapping: 1 to 1 for all existing data type names
            mapping = {k: k for k in arr.dtype.names}

        super().__init__(arr, mapping, known_dtypes=known_dtypes, from_idx=from_idx, to_idx=to_idx)

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
    def _check_source_arr(arr: np.ndarray) -> None:
        """Check that the input array is a structured, 1D numpy array."""

        if not isinstance(arr, np.ndarray):
            raise TypeError(f"Expected a numpy.ndarray; got {type(arr)}")

        if arr.ndim > 1:
            raise ValueError("Source array must be 1-dimensional")

        if not arr.dtype.names:
            raise ValueError("Input must be a structured numpy array")


class DictDataWrapper(SourceDataWrapper):
    """Wrap source data provided in the form of a dictionary of numpy arrays."""

    def __init__(self, data_dict: dict[str, np.ndarray], mapping: Optional[dict] = None,
                 known_dtypes: Optional[dict[str, numpy_dtype_type]] = None, from_idx: int = 0,
                 to_idx: Optional[int] = None) -> None:
        """Initialise DictDataWrapper.

        Args:
            data_dict       :   Source data - dict of numpy arrays.
            mapping         :   Mapping of target data type names on the keys found in the data dictionary.
                                Optional; if not provided, it is assumed that all items of the data dict should be included
                                in the target structured arrays.
            known_dtypes    :   Mapping of data type names on data types (if any are known). Does not have to contain
                                all dtypes. Can also be completely omitted. Missing data types are determined from
                                the data.
            from_idx        :   Index from which data should be loaded (or number of initial rows to ignore).
            to_idx          :   Index up to which data should be loaded.

        """

        self._check_source_dict(data_dict)

        if not mapping:
            # default mapping: 1 to 1 for all keys of the data dict
            mapping = {k: k for k in data_dict.keys()}

        super().__init__(data_dict, mapping, known_dtypes=known_dtypes, from_idx=from_idx, to_idx=to_idx)

    @staticmethod
    def _check_source_dict(data_dict: dict[str, np.ndarray]) -> None:
        """Check that all values of the source dictionary are numpy arrays."""

        if not isinstance(data_dict, dict):
            raise TypeError(f"Expected a dictionary, got {type(data_dict)}: {data_dict}")

        if not all(isinstance(k, str) for k in data_dict):
            raise TypeError(f"Source dictionary keys must be strings; got {', '.join(str(type(k)) for k in data_dict)}")

        if not all(isinstance(v, np.ndarray) for v in data_dict.values()):
            raise TypeError(f"Dict values must be numpy arrays; "
                            f"got {', '.join(str(type(v)) for v in data_dict.values())}")
