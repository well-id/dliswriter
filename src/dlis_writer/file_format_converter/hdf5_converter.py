from typing import Union, Generator, Optional
import h5py  # type: ignore  # untyped library
import logging
import numpy as np

from dlis_writer.file import DLISFile
from dlis_writer.logical_record.eflr_types import ChannelItem
from dlis_writer.utils.types import file_name_type, numpy_dtype_type


logger = logging.getLogger(__name__)


def yield_h5_datasets(h5_object: Union[h5py.File, h5py.Group]) -> Generator:
    """Traverse a HDF5 (h5py) object in a recursive manner and yield all datasets it contains.

    Args:
        h5_object   : HDF5 File or Group to traverse.

    Yields:
        h5py Dataset objects contained in the provided File or Group.
    """

    for key, value in h5_object.items():
        if isinstance(value, h5py.Dataset):
            yield value
        if isinstance(value, h5py.Group):
            yield from yield_h5_datasets(value)


def get_cast_dtype(dtype: numpy_dtype_type) -> numpy_dtype_type:
    """Determine whether data need to be cast to a different numpy dtype (not all types are supported).

    Returns the dtype the data should be cast to or the provided data type if no casting is required.
    """

    if dtype == np.int64:
        return np.int32
    if dtype == np.float16:
        return np.float32
    return dtype


def add_channels_from_h5_data(df: DLISFile, data: h5py.File, index_col_name: Optional[str] = None) -> list[ChannelItem]:
    """Add channels specifications to the file object, taking all datasets found in the provided HDF5 file."""

    channels = []

    def add_channel(dataset: h5py.Dataset) -> None:
        dataset_name = dataset.name
        ch = df.add_channel(
            dataset_name.split('/')[-1],
            dataset_name=dataset_name,
            cast_dtype=get_cast_dtype(dataset.dtype)
        )
        channels.append(ch)

    if index_col_name is not None:
        add_channel(data[index_col_name])  # add the index channel first

    for ds in yield_h5_datasets(data):
        if index_col_name is not None and (ds.name == index_col_name) or (ds.name == ('/' + index_col_name)):
            continue  # dataset already added
        add_channel(ds)

    return channels


def make_dlis_file_spec_from_hdf5(data_file_path: file_name_type, index_col_name: Optional[str] = None
                                  ) -> tuple[DLISFile, file_name_type]:
    """Create a DLISFile object according to the contents of the input data file."""

    df = DLISFile()
    df.add_origin("ORIGIN")

    with h5py.File(data_file_path, 'r') as h5f:
        channels = add_channels_from_h5_data(df, h5f, index_col_name=index_col_name)
    df.add_frame('MAIN', channels=channels)

    return df, data_file_path
