from pathlib import Path
import numpy as np
import logging
import os
from argparse import ArgumentParser
from timeit import timeit
from datetime import timedelta
from configparser import ConfigParser

from dlis_writer.file import DLISFile
from dlis_writer.logical_record.collections.logical_record_collection import LogicalRecordCollection
from dlis_writer.utils.loaders import load_hdf5, load_config
from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.utils.make_mock_data_hdf5 import create_data_file
from dlis_writer.writer.utils.compare_dlis_files import compare


logger = logging.getLogger(__name__)


class DLISWriter:
    default_config_file_name = Path(__file__).resolve().parent/'basic_config.ini',

    def __init__(self, data, config):
        self._data = data
        self._config = config

    @staticmethod
    def add_channel_config_from_data(data: np.ndarray, config: ConfigParser):
        sections = []

        for name in data.dtype.names:
            section = f"Channel-{name}"
            if section not in config.sections():
                config.add_section(section)
                config[section]['name'] = name
            sections.append(section)

        if sections:
            config['Frame']['channels'] = ', '.join(sections)

    @staticmethod
    def add_index_config(config: ConfigParser, depth_based=False):
        if 'index_type' not in config['Frame'].keys():
            config['Frame']['index_type'] = 'DEPTH' if depth_based else 'TIME'

        if 'spacing.units' not in config['Frame'].keys():
            config['Frame']['spacing.units'] = 'm' if depth_based else 's'

    @staticmethod
    def load_data(input_file_name):
        return load_hdf5(input_file_name)

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
        parser.add_argument('--depth-based', action='store_true', default=False,
                            help="Make a depth-based HDF5 file (default is time-based)")
        parser.add_argument('--channels-from-data', action='store_true', default=False,
                            help="Extend the provided config file with channel information from the data")

        return parser

    @classmethod
    def from_parser_args(cls, pargs):
        data = cls.load_data(pargs.input_file_name)

        if pargs.config:
            config_fn = pargs.config
            add_channels_from_data = pargs.channels_from_data
        else:
            config_fn = cls.default_config_file_name
            add_channels_from_data = True

        config = load_config(config_fn)
        if add_channels_from_data or ('channels' not in config['Frame'] and 'channels.value' not in config['Frame']):
            cls.add_channel_config_from_data(data, config)
        cls.add_index_config(config, depth_based=pargs.depth_based)

        writer = cls(data, config)

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
            depth_based=pargs.depth_based
        )
    else:
        tmp_file_name = None

    try:
        dlis_writer = DLISWriter.from_parser_args(pargs)
        dlis_writer.write_dlis_file(dlis_file_name=pargs.output_file_name)
    except Exception as exc:
        if tmp_file_name:
            os.remove(tmp_file_name)
        raise exc
    else:
        if tmp_file_name:
            os.remove(tmp_file_name)

    if pargs.reference_file_name is not None:
        compare_files(pargs.output_file_name, pargs.reference_file_name)

