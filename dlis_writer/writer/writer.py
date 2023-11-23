from pathlib import Path
import logging
import os
from argparse import ArgumentParser
from timeit import timeit
from datetime import timedelta

from dlis_writer.file import DLISFile
from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.dlis_file_comparator import compare
from dlis_writer.utils.source_data_objects import HDF5Interface
from dlis_writer.writer.dlis_config import DLISConfig


logger = logging.getLogger(__name__)


def write_dlis_file(data, config, dlis_file_name, visible_record_length=8192, **kwargs):
    def timed_func():
        dlis_file = DLISFile(visible_record_length=visible_record_length)
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
    parser.add_argument('--input-chunk-size', default=1e5, type=float,
                        help="Chunk size (number of rows) for the input data to be processed in")
    parser.add_argument('--output-chunk-size', default=2**32, type=float,
                        help="Size (in bytes) of the chunks in which the output file will be created")
    parser.add_argument('-ref', '--reference-file-name',
                        help="Another DLIS file to compare the created one against (at binary level)")
    parser.add_argument('--overwrite', action='store_true', default=False,
                        help="Allow overwriting existing output file")
    parser.add_argument('-vrl', '--visible-record-length', type=int, default=8192,
                        help="Maximum allowed visible record length")

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


def _check_write_access(p):
    if not os.access(p, os.W_OK):
        raise RuntimeError(f"Write permissions missing for directory: {p}")


def prepare_directory(output_file_name, overwrite=False):
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

    return save_dir


def main():
    install_logger(logger)

    pargs = make_parser().parse_args()

    prepare_directory(pargs.output_file_name, overwrite=pargs.overwrite)

    data, config = data_and_config_from_parser_args(pargs)
    write_dlis_file(
        data=data,
        config=config,
        dlis_file_name=pargs.output_file_name,
        input_chunk_size=int(pargs.input_chunk_size),
        output_chunk_size=int(pargs.output_chunk_size),
        visible_record_length=pargs.visible_record_length
    )

    if pargs.reference_file_name is not None:
        compare_files(pargs.output_file_name, pargs.reference_file_name)


if __name__ == '__main__':
    main()
