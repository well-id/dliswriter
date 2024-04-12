import numpy as np
import os
import h5py    # type: ignore  # untyped library
from pathlib import Path
from argparse import ArgumentParser
import logging
from typing import Union, Any

from dliswriter.utils.logging import install_colored_logger


logger = logging.getLogger(__name__)


def make_image(n_points: int, n_cols: int, divider: int = 11) -> np.ndarray:
    """Create a 2D array with synthetic data.

    Args:
        n_points    :   Number of rows.
        n_cols      :   Number of columns.
        divider     :   The array will be populated with remainders of division of values in range
                        (0, n_points x n_cols) by the divider. This creates an array with periodically repeating
                        integers, facilitating fast visual checks whether file data has been saved and read correctly.

    Returns:
        A numpy.ndarray of shape (n_points, n_cols) with values in range (0, divider).
    """

    return (np.arange(n_points * n_cols) % divider).reshape(n_points, n_cols) + 5 * np.random.rand(n_points, n_cols)


def _fill_in_data(h5_group: h5py.Group, n_points: int, n_images: int = 0, n_cols: int = 128,
                  time_based: bool = False) -> None:
    """Populate a HFD5 Group with synthetic datasets.

    This created 3 scalar (1D) datasets ('time' or 'depth', 'rpm', and 'col3') and as many 2D datasets as specified
    by the provided arguments.

    Args:
        h5_group    :   Group in an open HDF5 file to create the datasets in.
        n_points    :   Length (number of points/rows) for all datasets.
        n_images    :   Number of 2D datasets to be added.
        n_cols      :   Number of columns for each 2D dataset.
        time_based  :   If True, the first created dataset will be 'time'. Otherwise, it will be 'depth'.

    Returns:

    """

    if time_based:
        logger.debug("Creating time dataset")
        h5_group.create_dataset('time', data=0.5 * np.arange(n_points))
    else:
        logger.debug("Creating depth dataset")
        h5_group.create_dataset('depth', data=2500 + 0.1 * np.arange(n_points))

    logger.debug("Creating two more linear datasets")
    h5_group.create_dataset('rpm', data=10 * np.sin(np.linspace(0, 1e4 * np.pi, n_points)))
    h5_group.create_dataset('col3', data=np.arange(n_points, dtype=np.float32))

    for i in range(n_images):
        logger.debug(f"Creating image dataset {i+1}/{n_images}")
        h5_group.create_dataset(
            f'image{i}', data=make_image(n_points, n_cols, divider=int(10 + (n_cols - 11) * np.random.rand())))


def create_data_file(n_points: int, fpath: Union[str, os.PathLike[str]], overwrite: bool = False,
                     **kwargs: Any) -> None:
    """Create a synthetic HDF5 data file.

    Args:
        n_points    :   Number of rows for each dataset in the file.
        fpath       :   Path to the file to be created.
        overwrite   :   Used if the file already exists. If True, allow overwriting it. Otherwise, raise a RuntimeError.
        **kwargs    :   Additional keyword arguments, including:
                            n_images    :   Number of 2D datasets to be added.
                            n_cols      :   Number of columns for each 2D dataset.
                            time_based  :   If True, the first created dataset will be 'time', otherwise - 'depth'.
    """

    if os.path.exists(fpath):
        if overwrite:
            logger.info(f"Removing existing HDF5 file at {fpath}")
            os.remove(fpath)
        else:
            raise RuntimeError(f"File '{fpath}' already exists. Cannot overwrite file.")

    exception = None

    logger.info(f"Creating a HDF5 file at {fpath}")
    h5_file = h5py.File(fpath, 'w', track_order=True)
    try:
        group = h5_file.create_group('contents', track_order=True)
        _fill_in_data(group, n_points, **kwargs)
    except Exception as exc:
        exception = exc
    finally:
        h5_file.flush()
        h5_file.close()

    if exception:
        raise exception

    logger.info(f"Fake data with {n_points} points saved to file '{fpath}'")


def main() -> None:
    """Create a synthetic HDF5 data file based on information from command line arguments."""

    parser = ArgumentParser("Creating HFD5 file with mock well data")
    parser.add_argument('-n', '--n-points', help='Number of data points', type=float, default=5e3)
    parser.add_argument('-fn', '--file-name', help='Output file name')
    parser.add_argument('-ni', '--n-images', type=int, default=0, help='Number of 2D data sets to add')
    parser.add_argument('-nc', '--n-cols', type=int, default=128,
                        help='Number of columns for each of the added 2D data sets')
    parser.add_argument('--depth-based', action='store_true', default=False,
                        help="Make a depth-based HDF5 file (default is time-based)")
    parser.add_argument('--overwrite', action='store_true', default=False,
                        help='Allow to overwrite existing hdf5 file of the same name')
    parser_args = parser.parse_args()

    if (file_name := parser_args.file_name) is None:
        file_name = 'mock_data.hdf5'
    if len(Path(file_name).parts) == 1 and not file_name.startswith('./'):
        file_name = Path(__file__).resolve().parent.parent / 'resources' / file_name
        os.makedirs(file_name.parent, exist_ok=True)

    create_data_file(
        n_points=int(parser_args.n_points),
        fpath=file_name,
        n_images=parser_args.n_images,
        n_cols=parser_args.n_cols,
        overwrite=parser_args.overwrite,
        depth_based=parser_args.depth_based
    )


if __name__ == '__main__':
    install_colored_logger(logger)

    main()
