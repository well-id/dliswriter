from pathlib import Path
import logging
import os
from argparse import ArgumentParser, Namespace
from timeit import timeit
from datetime import timedelta
from typing import Union
from configparser import ConfigParser

from dlis_writer.writer.writer import DLISWriter
from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.dlis_file_comparator import compare
from dlis_writer.utils.source_data_objects import HDF5Interface, SourceDataObject
from dlis_writer.writer.dlis_config import DLISConfig


logger = logging.getLogger(__name__)

path_type = Union[str, os.PathLike[str]]


def write_dlis_file(data: SourceDataObject, config: ConfigParser, dlis_file_name: path_type,
                    visible_record_length: int = 8192, **kwargs):
    """Create a DLIS file from data and specification info.

    Args:
        data                    :   The source data, wrapped in a (subclass of) SourceDataObject.
        config                  :   Config object with specification on what to include in the DLIS file.
        dlis_file_name          :   Name of the file to be created.
        visible_record_length   :   Maximal length of visible records to be created in the file.
        **kwargs                :   Additional keyword arguments, passed to DLISFile.create_dlis; this includes:
                                        input_chunk_size    :   Size of the chunks (in rows) in which input data
                                                                will be loaded to be processed.
                                        output_chunk_size   :   Size of the buffers accumulating file bytes
                                                                before file write action is called.
    """

    def timed_func():
        """Perform the action of creating a DLIS file.

        This function is used in a timeit call to time the file creation.
        """

        dlis_file = DLISWriter(visible_record_length=visible_record_length)
        dlis_file.create_dlis_from_config_and_data(data=data, config=config, filename=dlis_file_name, **kwargs)

    exec_time = timeit(timed_func, number=1)
    logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")


def make_parser(require_input_fname: bool = True) -> ArgumentParser:
    """Create a command line argument parser for a specification of the DLIS file to be created.

    Args:
        require_input_fname :   If True, set 'input_file_name' argument as required.

    Returns:
         The configured ArgumentParser instance.
    """

    parser = ArgumentParser("DLIS file creation")
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


def data_and_config_from_parser_args(pargs: Namespace) -> tuple[HDF5Interface, ConfigParser]:
    """Create a SourceDataObject and a ConfigParser object based on information from the arg parser.

    Args:
        pargs   :   Parsed command line arguments.

    Returns:
        - HDF5Interface (a SourceDataObject subclass) object containing the data from the HDF5 file.
        - ConfigParser object, created from the provided config file and/or data.
    """

    if pargs.config:
        logger.info(f"Loading config file from {pargs.config}")
        config = DLISConfig.from_config_file(pargs.config)
    else:
        logger.info("Config file path not provided; creating a config based on the data")
        config = DLISConfig.from_h5_data_file(pargs.input_file_name)

    data = HDF5Interface.from_config(pargs.input_file_name, config.config)

    if not pargs.config and pargs.channels_from_data:
        config.add_channel_config_from_h5_data(data.data_source)
        config.add_index_config(time_based=pargs.time_based)

    return data, config.config


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


def main():
    """Define an argument parser, parse the args and create a DLIS file based on these."""

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
