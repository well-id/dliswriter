from pathlib import Path
import logging
import os
from argparse import ArgumentParser

from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.utils.make_mock_data_hdf5 import create_data_file
from dlis_writer.writer.writer import (write_dlis_file, make_parser as make_parent_parser,
                                       data_and_config_from_parser_args, prepare_directory)


logger = logging.getLogger(__name__)


def make_parser():
    parser = ArgumentParser("DLIS file creation from synthetic data",
                            parents=[make_parent_parser(add_help=False, require_input_fname=False)])

    parser.add_argument('-n', '--n-points', help='Number of data points', type=float, default=10e3)
    parser.add_argument('-ni', '--n-images', type=int, default=0,
                        help='Number of 2D data sets to add (ignored if input file is specified)')
    parser.add_argument('-nc', '--n-cols', type=int, default=128,
                        help='No. columns for each of the added 2D data sets (ignored if input file specified)')

    return parser


def create_tmp_data_file_from_pargs(file_name, pargs):
    create_data_file(
        fpath=file_name,
        n_points=int(pargs.n_points),
        n_images=pargs.n_images,
        n_cols=pargs.n_cols,
        time_based=pargs.time_based,
        overwrite=True
    )


def main():
    pargs = make_parser().parse_args()

    prepare_directory(pargs)

    tmp_file_name = Path('./_tmp.h5').resolve()  # TODO: save in the same directory as the output file
    pargs.input_file_name = tmp_file_name
    create_tmp_data_file_from_pargs(tmp_file_name, pargs)

    exception = None
    try:
        data, config = data_and_config_from_parser_args(pargs)
        write_dlis_file(
            data=data,
            config=config,
            dlis_file_name=pargs.output_file_name,
            chunk_rows=int(pargs.chunk_rows)
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
    install_logger(logger)
    main()
