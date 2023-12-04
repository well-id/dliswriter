from pathlib import Path
import logging
import os
from argparse import ArgumentParser, Namespace

from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.synthetic_data_generator import create_data_file
from dlis_writer.writer.write_dlis_file import (write_dlis_file, make_parser as make_parent_parser,
                                                data_and_config_from_parser_args, prepare_directory, path_type)


logger = logging.getLogger(__name__)


def make_parser() -> ArgumentParser:
    """Define an argument parser for defining the DLIS file to be created."""

    parser = make_parent_parser(require_input_fname=False)

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
    """Generate a synthetic data file. Use it as the source data for writing a DLIS file."""

    install_logger(logger)

    pargs = make_parser().parse_args()

    prepare_directory(pargs.output_file_name, overwrite=pargs.overwrite)

    tmp_file_name = Path(pargs.output_file_name).resolve().parent/'_tmp.h5'
    pargs.input_file_name = tmp_file_name
    create_tmp_data_file_from_pargs(tmp_file_name, pargs)

    exception = None
    try:
        data, config = data_and_config_from_parser_args(pargs)
        write_dlis_file(
            data=data,
            config=config,
            dlis_file_name=pargs.output_file_name,
            input_chunk_size=int(pargs.input_chunk_size),
            output_chunk_size=int(pargs.output_chunk_size),
            visible_record_length=pargs.visible_record_length
        )
    except Exception as exc:
        exception = exc
    finally:
        try:
            os.remove(pargs.input_file_name)
        except Exception as exc2:
            logger.error(f"Error trying to remove temporary hdf5 data file: '{exc2}'")
    if exception:
        raise exception


if __name__ == '__main__':
    main()
