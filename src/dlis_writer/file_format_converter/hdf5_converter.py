from typing import Union, Generator
import h5py  # type: ignore  # untyped library
import logging

from dlis_writer.file import DLISFile
from dlis_writer.logical_record.eflr_types import ChannelItem
from dlis_writer.utils.types import file_name_type


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


def add_channels_from_h5_data(df: DLISFile, data: h5py.File) -> list[ChannelItem]:
    """Add channels specifications to the file object, taking all datasets found in the provided HDF5 file."""

    channels = []

    for dataset in yield_h5_datasets(data):
        dataset_name = dataset.name
        channel_name = dataset_name.split('/')[-1]
        ch = df.add_channel(
            channel_name,
            dataset_name=dataset_name
        )
        channels.append(ch)

    return channels


def make_dlis_file_spec_from_hdf5(data_file_path: file_name_type) -> tuple[DLISFile, file_name_type]:
    df = DLISFile()
    df.add_origin("ORIGIN", file_set_number=1)

    with h5py.File(data_file_path, 'r') as h5f:
        channels = add_channels_from_h5_data(df, h5f)
    df.add_frame('MAIN', channels=channels)

    return df, data_file_path
