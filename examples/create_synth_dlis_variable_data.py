import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.synthetic_data_generator import create_data_file

from utils import path_type, prepare_directory


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


def create_tmp_data_file_from_pargs(file_name: path_type, pargs: Namespace):
    """Generate synthetic data and store it in a HDF5 file.

    Args:
        file_name   :   Name for the data file to be created.
        pargs       :   Parsed command line arguments with specification of the data to be generated.

    Returns:

    """

    create_data_file(
        fpath=file_name,
        n_points=int(pargs.n_points),
        n_images=pargs.n_images,
        n_cols=pargs.n_cols,
        time_based=pargs.time_based,
        overwrite=True
    )


def main():
    install_logger(logger)

    pargs = make_parser().parse_args()

    prepare_directory(pargs.output_file_name, overwrite=pargs.overwrite)

    tmp_file_name = Path(pargs.output_file_name).resolve().parent/'_tmp.h5'
    pargs.input_file_name = tmp_file_name
    create_tmp_data_file_from_pargs(tmp_file_name, pargs)


if __name__ == '__main__':
    main()
