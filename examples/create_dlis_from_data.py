import logging
from argparse import ArgumentParser

from dlis_writer.utils.logging import install_colored_logger

from utils import prepare_directory, make_dlis_file_spec


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

    return parser


def main() -> None:
    install_colored_logger(logging.getLogger('dlis_writer'))

    pargs = make_parser().parse_args()

    prepare_directory(pargs.output_file_name, overwrite=pargs.overwrite)

    dlis_file = make_dlis_file_spec(pargs.input_file_name)
    dlis_file.write(
        pargs.output_file_name,
        data=pargs.input_file_name,
        input_chunk_size=int(pargs.input_chunk_size) if pargs.input_chunk_size else None,
        output_chunk_size=int(pargs.output_chunk_size) if pargs.output_chunk_size else None,
    )


if __name__ == '__main__':
    main()
