from pathlib import Path
import logging
import os
from argparse import ArgumentParser
from timeit import timeit
from datetime import timedelta
from configparser import ConfigParser

from dlis_writer.file import DLISFile
from dlis_writer.logical_record.collections.logical_record_collection import LogicalRecordCollection
from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.utils.make_mock_data_hdf5 import create_data_file
from dlis_writer.writer.utils.compare_dlis_files import compare
from dlis_writer.utils.source_data_objects import HDF5Interface, SourceDataObject
from dlis_writer.writer.config_from_data import DLISConfig


logger = logging.getLogger(__name__)


class DLISWriter:

    def __init__(self, data: SourceDataObject, config: ConfigParser):
        self._data = data
        self._config = config

    def write_dlis_file(self, dlis_file_name):
        def timed_func():
            logical_records = LogicalRecordCollection.from_config_and_data(self._config, self._data)

            dlis_file = DLISFile()
            dlis_file.write_dlis(logical_records, dlis_file_name)

        exec_time = timeit(timed_func, number=1)
        logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")

    @classmethod
    def make_parser(cls):
        parser = ArgumentParser("DLIS file creation - minimal working example")
        pg = parser.add_mutually_exclusive_group()
        pg.add_argument('-n', '--n-points', help='Number of data points', type=float, default=10e3)
        pg.add_argument('-ifn', '--input-file-name', help='Input file name')

        parser.add_argument('-c', '--config', help="Path to config file specifying metadata")
        parser.add_argument('-ofn', '--output-file-name', help='Output file name')
        parser.add_argument('-ni', '--n-images', type=int, default=0,
                            help='Number of 2D data sets to add (ignored if input file is specified)')
        parser.add_argument('-nc', '--n-cols', type=int, default=128,
                            help='No. columns for each of the added 2D data sets (ignored if input file specified)')
        parser.add_argument('--time-based', action='store_true', default=False,
                            help="Make a time-based DLIS file (default is depth-based)")
        parser.add_argument('--channels-from-data', action='store_true', default=False,
                            help="Extend the provided config file with channel information from the data")

        return parser

    @classmethod
    def from_parser_args(cls, pargs):

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

        writer = cls(data, config.config)

        return writer


def compare_files(output_file_name, reference_file_name):
    logger.info(f"Comparing the newly created DLIS file with a reference file: {reference_file_name}")
    equal = compare(output_file_name, reference_file_name, verbose=True)
    if equal:
        logger.info("Files are equal")
    else:
        logger.warning("Files are NOT equal")


if __name__ == '__main__':
    install_logger(logger)

    parser = DLISWriter.make_parser()
    parser.add_argument('-ref', '--reference-file-name',
                        help="Another DLIS file to compare the created one against (at binary level)")
    parser.set_defaults(
        output_file_name=Path(__file__).resolve().parent.parent/'tests/outputs/mwe_fake_dlis.DLIS'
    )
    pargs = parser.parse_args()

    os.makedirs(Path(pargs.output_file_name).parent, exist_ok=True)

    if (input_file_name := pargs.input_file_name) is None:
        tmp_file_name = Path('./_tmp.h5').resolve()
        pargs.input_file_name = tmp_file_name
        create_data_file(
            fpath=tmp_file_name,
            n_points=int(pargs.n_points),
            n_images=pargs.n_images,
            n_cols=pargs.n_cols,
            time_based=pargs.time_based,
            overwrite=True  # TODO
        )
    else:
        tmp_file_name = None

    exception = None
    try:
        dlis_writer = DLISWriter.from_parser_args(pargs)
        dlis_writer.write_dlis_file(dlis_file_name=pargs.output_file_name)
    except Exception as exc:
        exception = exc
    finally:
        if tmp_file_name:
            try:
                os.remove(tmp_file_name)
            except Exception as exc2:
                logger.error(f"Error trying to remove temporary hdf5 data file: '{exc2}'")
    if exception:
        raise exception

    if pargs.reference_file_name is not None:
        compare_files(pargs.output_file_name, pargs.reference_file_name)

