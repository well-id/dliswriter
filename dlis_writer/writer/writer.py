from pathlib import Path
import logging
import os
from argparse import ArgumentParser
from timeit import timeit
from datetime import timedelta

from dlis_writer.file import DLISFile
from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.utils.compare_dlis_files import compare
from dlis_writer.utils.source_data_objects import HDF5Interface
from dlis_writer.writer.config_from_data import DLISConfig


logger = logging.getLogger(__name__)


def write_dlis_file(data, config, dlis_file_name, **kwargs):
    def timed_func():
        dlis_file = DLISFile()
        dlis_file.create_dlis(data=data, config=config, filename=dlis_file_name, **kwargs)

    exec_time = timeit(timed_func, number=1)
    logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")


def make_parser(add_help=True, require_input_fname=True):
    parser = ArgumentParser("DLIS file creation", add_help=add_help)
    parser.add_argument('-ifn', '--input-file-name', help='Input file name', required=require_input_fname)
    parser.add_argument('-c', '--config', help="Path to config file specifying metadata")
    parser.add_argument('-ofn', '--output-file-name', help='Output file name', required=True)
    parser.add_argument('--time-based', action='store_true', default=False,
                        help="Make a time-based DLIS file (default is depth-based)")
    parser.add_argument('--channels-from-data', action='store_true', default=False,
                        help="Extend the provided config file with channel information from the data")
    parser.add_argument('--chunk-rows', default=1e5, type=float,
                        help="Chunk size (number of rows) for the source file to be processed in")
    parser.add_argument('-ref', '--reference-file-name',
                        help="Another DLIS file to compare the created one against (at binary level)")

    return parser


def data_and_config_from_parser_args(pargs):
    if pargs.config:
        logger.info(f"Loading config file from {pargs.config}")
        config = DLISConfig.from_config_file(pargs.config)
    else:
        logger.info("Config file path not provided; creating a config based on the data")
        config = DLISConfig.from_h5_data_file(pargs.input_file_name)

    data = HDF5Interface.from_config(pargs.input_file_name, config.config)

    if not pargs.config and pargs.channels_from_data:
        config.add_channel_config_from_data(data)
        config.add_index_config(time_based=pargs.time_based)

    return data, config.config


def compare_files(output_file_name, reference_file_name):
    logger.info(f"Comparing the newly created DLIS file with a reference file: {reference_file_name}")
    equal = compare(output_file_name, reference_file_name, verbose=True)
    if equal:
        logger.info("Files are equal")
    else:
        logger.warning("Files are NOT equal")


def prepare_directory(pargs):
    os.makedirs(Path(pargs.output_file_name).parent, exist_ok=True)
    # TODO: check write access
    # TODO: check for existing file


def main():
    pargs = make_parser().parse_args()

    prepare_directory(pargs)

    data, config = data_and_config_from_parser_args(pargs)
    write_dlis_file(
        data=data,
        config=config,
        dlis_file_name=pargs.output_file_name,
        chunk_rows=int(pargs.chunk_rows)
    )

    if pargs.reference_file_name is not None:
        compare_files(pargs.output_file_name, pargs.reference_file_name)


if __name__ == '__main__':
    install_logger(logger)
    main()
