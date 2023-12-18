import os
from pathlib import Path
from typing import Union
import h5py  # type: ignore  # untyped library
import logging

from dlis_writer.misc.dlis_file_comparator import compare
from dlis_writer.file import DLISFile
from dlis_writer.utils.converters import ReprCodeConverter


logger = logging.getLogger(__name__)

path_type = Union[str, os.PathLike[str]]


def compare_files(output_file_name: path_type, reference_file_name: path_type):
    """Compare two DLIS files (whose filenames are provided as the two arguments) at binary level.

    Display the verdict in the log messages.
    """

    logger.info(f"Comparing the newly created DLIS file with a reference file: {reference_file_name}")
    equal = compare(output_file_name, reference_file_name, verbose=True)
    if equal:
        logger.info("Files are equal")
    else:
        logger.warning("Files are NOT equal")


def _check_write_access(p: path_type):
    """Check if the provided path supports write action. Raise a RuntimeError otherwise."""

    if not os.access(p, os.W_OK):
        raise RuntimeError(f"Write permissions missing for directory: {p}")


def prepare_directory(output_file_name: path_type, overwrite: bool = False):
    """Prepare directory for the output file.

    Create up to 1 top level on the path. Make sure the directory allows writing.
    Check if a file of the given name already exists.

    Args:
        output_file_name    :   Name of the file to be created.
        overwrite           :   Used if the file already exists. If True, include a warning in the logs and overwrite
                                the file. If False, raise a RuntimeError.
    """

    output_file_name = Path(output_file_name).resolve()
    save_dir = output_file_name.parent
    parent_dir = save_dir.parent

    if not parent_dir.exists():
        raise RuntimeError(f"Directory {parent_dir} does not exist")

    _check_write_access(parent_dir)

    os.makedirs(save_dir, exist_ok=True)
    _check_write_access(save_dir)

    if os.path.exists(output_file_name):
        if overwrite:
            logger.warning(f"Output file at {output_file_name} will be overwritten")
        else:
            raise RuntimeError(f"Cannot overwrite existing file at {output_file_name}")


def yield_h5_datasets(h5_object: Union[h5py.File, h5py.Group]):
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


def add_channels_from_h5_data(df: DLISFile, data: h5py.File):
    """Add channels specifications to the file object, taking all datasets found in the provided HDF5 file."""

    channels = []

    for dataset in yield_h5_datasets(data):
        dataset_name = dataset.name
        channel_name = dataset_name.split('/')[-1]
        ch = df.add_channel(
            channel_name,
            dataset_name=dataset_name,
            representation_code=ReprCodeConverter.determine_repr_code_from_numpy_dtype(dataset.dtype).value
        )
        channels.append(ch)

    return channels


def make_dlis_file_spec(data_file_path: Path) -> DLISFile:
    df = DLISFile()
    with h5py.File(data_file_path, 'r') as h5f:
        channels = add_channels_from_h5_data(df, h5f)
    df.add_frame('MAIN', channels=channels)

    return df
