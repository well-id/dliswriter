"""Create a DLIS file from a HDF5 data file.

All channels etc. are added automatically from the contents of the data file.
"""

import logging
from argparse import ArgumentParser

from dlis_writer.utils.logging import install_colored_logger
from dlis_writer.file_format_converter.file_format_converter import write_dlis_from_data_file
from dlis_writer.misc.dlis_file_comparator import compare
from dlis_writer.utils.types import file_name_type

from utils import prepare_directory


logger = logging.getLogger(__name__)


def make_parser() -> ArgumentParser:
    """Define an argument parser for defining the DLIS file to be created."""

    parser = ArgumentParser("DLIS file creation")
    parser.add_argument('-ifn', '--input-file-name', help='Input file name', required=True)
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
    parser.add_argument('-ref', '--reference-file-name',
                        help="Reference file to compare the new DLIS against")
    parser.add_argument('--index-col', help="Name pointing to the index dataset (e.g. depth)")

    return parser


def compare_files(output_file_name: file_name_type, reference_file_name: file_name_type) -> None:
    """Compare two DLIS files (whose filenames are provided as the two arguments) at binary level.

    Display the verdict in the log messages.
    """

    logger.info(f"Comparing the newly created DLIS file with a reference file: {reference_file_name}")
    equal = compare(output_file_name, reference_file_name, verbose=True)
    if equal:
        logger.info("Files are equal")
    else:
        logger.warning("Files are NOT equal")


def main() -> None:
    install_colored_logger(logging.getLogger('dlis_writer'))

    pargs = make_parser().parse_args()

    prepare_directory(pargs.output_file_name, overwrite=pargs.overwrite)

    write_dlis_from_data_file(
        data_file_path=pargs.input_file_name,
        output_file_path=pargs.output_file_name,
        input_chunk_size=int(pargs.input_chunk_size),
        output_chunk_size=int(pargs.output_chunk_size),
        index_col_name=pargs.index_col
    )

    if pargs.reference_file_name:
        compare_files(pargs.output_file_name, pargs.reference_file_name)


if __name__ == '__main__':
    main()
