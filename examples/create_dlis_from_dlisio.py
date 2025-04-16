import logging
from dlisio import dlis    # type: ignore  # untyped library
import numpy as np

from argparse import ArgumentParser
from dliswriter.utils.import_from_dlisio import create_from_dlisio    # type: ignore  # untyped library

logger = logging.getLogger(__name__)


def make_parser() -> ArgumentParser:
    """Define an argument parser for defining the DLIS file to be created."""

    parser = ArgumentParser("DLIS file creation")
    parser.add_argument('-ifn', '--input-file-name', help='Intput file name', required=True)
    parser.add_argument('-ofn', '--output-file-name', help='Output file name', required=True)
    parser.add_argument('-min', '--minimal-mode', help='If True, a minimal mode is apllyed, writing '
                        'solely the logical files, origins, frames and channels', required=True)

    return parser


def main() -> None:
    """
    - This example reads a DLIS file with dlisio and re-writes it with dliswriter
        - DLIS specification is complex and some files may fail. Note that some users don't need all data.
        You can call this script with --minimal-mode True to pass along just the logical files, origins, frames and
        channels.
    - It is also checked if the numerical log data in the output file matches exactly that of the input file
    """

    pargs = make_parser().parse_args()

    # 1. Import a DLIS file using dlisio library
    dlisio_logical_files = dlis.load(pargs.input_file_name)

    # 2. Re-create the DLIS file in memory as a dliswriter object
    output_dlis_file = create_from_dlisio(dlisio_logical_files, pargs.minimal_mode)

    # 3. Write the new DLIS file to disk (hopefully with the same contents)
    output_dlis_file.write(pargs.output_file_name)

    # 4. Checking if log numerical data is preserved
    compare_log_data(dlisio_logical_files, dlis.load(pargs.output_file_name))


def compare_log_data(in_logical_files, reread_logical_files):

    assert len(in_logical_files) == len(reread_logical_files)

    for idx_lf, lf in enumerate(reread_logical_files):
        assert int(in_logical_files[idx_lf].fileheader.sequencenr) == int(
            reread_logical_files[idx_lf].fileheader.sequencenr
        )
        assert (
            in_logical_files[idx_lf].fileheader.id
            == reread_logical_files[idx_lf].fileheader.id
        )
        assert (
            in_logical_files[idx_lf].fileheader.name
            == reread_logical_files[idx_lf].fileheader.name
        )

        for idx_o, o in enumerate(lf.origins):
            # NOTE - creation_time not compared because it is set anew in output file
            in_origin = in_logical_files[idx_lf].origins[idx_o]
            out_origin = reread_logical_files[idx_lf].origins[idx_o]

            assert in_origin.file_set_nr == out_origin.file_set_nr
            assert in_origin.file_id == out_origin.file_id
            assert in_origin.file_nr == out_origin.file_nr
            assert in_origin.well_name == out_origin.well_name
            assert in_origin.file_set_name == out_origin.file_set_name
            assert in_origin.origin == out_origin.origin
            assert in_origin.file_type == out_origin.file_type
            assert in_origin.product == out_origin.product
            assert in_origin.version == out_origin.version
            assert in_origin.programs == out_origin.programs
            assert in_origin.order_nr == out_origin.order_nr

            # NOTE - dliswriter expects int, dlisio a list. rp66v1 doesn't specify
            if (len(in_origin.descent_nr)):
                assert in_origin.descent_nr[0] == out_origin.descent_nr[0]
            else:
                assert len(out_origin.descent_nr) == 0

            # NOTE - dliswriter expects int, dlisio a list. rp66v1 doesn't specify
            if (len(in_origin.run_nr)):
                assert in_origin.run_nr[0] == out_origin.run_nr[0]
            else:
                assert len(out_origin.run_nr) == 0

            assert in_origin.well_id == out_origin.well_id
            assert in_origin.field_name == out_origin.field_name
            assert in_origin.producer_code == out_origin.producer_code
            assert in_origin.producer_name == out_origin.producer_name
            assert in_origin.company == out_origin.company
            assert in_origin.namespace_name == out_origin.namespace_name
            assert in_origin.namespace_version == out_origin.namespace_version

        assert len(in_logical_files[idx_lf].frames) == len(
            reread_logical_files[idx_lf].frames
        )

        for idx_fr, fr in enumerate(lf.frames):
            in_frame = in_logical_files[idx_lf].frames[idx_fr]
            out_frame = reread_logical_files[idx_lf].frames[idx_fr]

            assert in_frame.name == out_frame.name
            assert in_frame.description == out_frame.description
            assert in_frame.origin == out_frame.origin

            assert len(in_frame.channels) == len(out_frame.channels)

            for idx_c, c in enumerate(lf.channels):
                in_channel = in_logical_files[idx_lf].channels[idx_c]
                out_channel = reread_logical_files[idx_lf].channels[idx_c]

                assert in_channel.dtype.base == out_channel.dtype.base
                assert in_channel.long_name == out_channel.long_name
                assert in_channel.units == out_channel.units
                assert in_channel.origin == out_channel.origin
                assert in_channel.dimension == out_channel.dimension
                assert in_channel.element_limit == out_channel.element_limit

                logger.debug("Comparing in and out actual curves data...")

                # np.testing.assert_allclose(in_channel.curves(), out_channel.curves(), rtol=0.5, atol=5e-06)
                np.testing.assert_equal(in_channel.curves(), out_channel.curves())

    logger.info("Success - Origins, Channels and Frames were preserved.")


if __name__ == '__main__':
    main()
