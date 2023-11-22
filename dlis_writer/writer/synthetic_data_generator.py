import numpy as np
import os
import h5py
from pathlib import Path
from argparse import ArgumentParser
import logging

from dlis_writer.utils.logging import install_logger


logger = logging.getLogger(__name__)


def make_image(n_points, n_cols, divider=11):
    return (np.arange(n_points * n_cols) % divider).reshape(n_points, n_cols) + 5 * np.random.rand(n_points, n_cols)


def _fill_in_data(h5_group, n_points: int, n_images: int = 0, n_cols: int = 128, time_based=False) -> np.ndarray:

    if time_based:
        logger.debug("Creating time dataset")
        h5_group.create_dataset('time', data=0.5 * np.arange(n_points))
    else:
        logger.debug("Creating depth dataset")
        h5_group.create_dataset('depth', data=2500 + 0.1 * np.arange(n_points))

    logger.debug("Creating two more linear datasets")
    h5_group.create_dataset('rpm', data=10 * np.sin(np.linspace(0, 1e4 * np.pi, n_points)))
    h5_group.create_dataset('col3', data=np.arange(n_points, dtype=np.float16))

    for i in range(n_images):
        logger.debug(f"Creating image dataset {i+1}/{n_images}")
        h5_group.create_dataset(
            f'image{i}', data=make_image(n_points, n_cols, divider=int(10 + (n_cols - 11) * np.random.rand())))


def create_data_file(n_points, fpath, overwrite=False, **kwargs):
    if fpath.exists():
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


def main():
    install_logger(logger)

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
    main()
