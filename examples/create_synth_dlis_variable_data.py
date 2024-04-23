"""Create synthetic data with a given number of rows and optionally, given number and width of images (2D data).
Define channels for the data and write them into a DLIS file.
"""

import logging
from argparse import ArgumentParser
from pathlib import Path
import numpy as np

from dliswriter import DLISFile, enums

from utils import prepare_directory, install_colored_logger


logger = logging.getLogger(__name__)


def make_parser() -> ArgumentParser:
    """Define an argument parser for defining the DLIS file to be created."""

    parser = ArgumentParser("DLIS file creation")
    parser.add_argument('-ofn', '--output-file-name', help='Output file name', required=True)
    parser.add_argument('--time-based', action='store_true', default=False,
                        help="Make a time-based DLIS file (default is depth-based)")
    parser.add_argument('--input-chunk-size', default=1e5, type=float,
                        help="Chunk size (number of rows) for the input data to be processed in")
    parser.add_argument('--output-chunk-size', default=2 ** 32, type=float,
                        help="Size (in bytes) of the chunks in which the output file will be created")
    parser.add_argument('--overwrite', action='store_true', default=False,
                        help="Allow overwriting existing output file")
    parser.add_argument('-vrl', '--visible-record-length', type=int, default=8192,
                        help="Maximum allowed visible record length")

    parser.add_argument('-n', '--n-points', help='Number of data points', type=float, default=10e3)
    parser.add_argument('-ni', '--n-images', type=int, default=0,
                        help='Number of 2D data sets to add (ignored if input file is specified)')
    parser.add_argument('-nc', '--n-cols', type=int, default=128,
                        help='No. columns for each of the added 2D data sets (ignored if input file specified)')

    return parser


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


def create_dlis_spec(n_points: int, n_images: int = 0, n_cols: int = 128, time_based: bool = False) -> DLISFile:
    """Create a DLIS file specification (DLISFile object) according to the arguments setup.

    This created 3 scalar (1D) datasets ('time' or 'depth', 'rpm', and 'col3') and as many 2D datasets as specified
    by the provided arguments.

    Args:
        n_points    :   Length (number of points/rows) for all datasets.
        n_images    :   Number of 2D datasets to be added.
        n_cols      :   Number of columns for each 2D dataset.
        time_based  :   If True, the first created dataset will be 'time'. Otherwise, it will be 'depth'.
    """

    df = DLISFile()
    df.add_origin("ORIGIN")

    if time_based:
        logger.debug("Creating time dataset")
        index = df.add_channel("TIME", data=0.5 * np.arange(n_points))
        index_type = enums.FrameIndexType.NON_STANDARD
    else:
        logger.debug("Creating depth dataset")
        index = df.add_channel('DEPTH', data=2500 + 0.1 * np.arange(n_points))
        index_type = enums.FrameIndexType.BOREHOLE_DEPTH

    channels = [index]

    for i in range(n_images):
        logger.debug(f"Creating image dataset {i+1}/{n_images}")
        ch = df.add_channel(
            f'IMAGE{i}', data=make_image(n_points, n_cols, divider=int(10 + (n_cols - 11) * np.random.rand())))
        channels.append(ch)

    df.add_frame("MAIN-FRAME", channels=channels, index_type=index_type)

    return df


def main() -> None:
    install_colored_logger(logging.getLogger('dliswriter'))

    pargs = make_parser().parse_args()

    prepare_directory(pargs.output_file_name, overwrite=pargs.overwrite)

    tmp_file_name = Path(pargs.output_file_name).resolve().parent/'_tmp.h5'
    pargs.input_file_name = tmp_file_name

    df = create_dlis_spec(
        n_points=int(pargs.n_points),
        n_images=pargs.n_images,
        n_cols=pargs.n_cols,
        time_based=pargs.time_based
    )

    df.write(
        pargs.output_file_name,
        input_chunk_size=int(pargs.input_chunk_size),
        output_chunk_size=int(pargs.output_chunk_size)
    )


if __name__ == '__main__':
    main()
