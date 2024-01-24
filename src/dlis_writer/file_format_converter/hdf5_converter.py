from typing import Union, Generator
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


def add_channels_from_h5_data(df: DLISFile, data: h5py.File) -> list[ChannelItem]:
    """Add channels specifications to the file object, taking all datasets found in the provided HDF5 file."""

    channels = []

    for dataset in yield_h5_datasets(data):
        dataset_name = dataset.name
        channel_name = dataset_name.split('/')[-1]
        ch = df.add_channel(
            channel_name,
            dataset_name=dataset_name,
            cast_dtype=get_cast_dtype(dataset.dtype)
        )
        channels.append(ch)

    return channels


def make_dlis_file_spec_from_hdf5(data_file_path: file_name_type) -> tuple[DLISFile, file_name_type]:
    """Create a DLISFile object according to the contents of the input data file."""

    df = DLISFile()
    df.add_origin("ORIGIN", file_set_number=1)

    with h5py.File(data_file_path, 'r') as h5f:
        channels = add_channels_from_h5_data(df, h5f)
    df.add_frame('MAIN', channels=channels)

    return df, data_file_path