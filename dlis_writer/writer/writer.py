from pathlib import Path
import numpy as np
import logging
import os
from argparse import ArgumentParser
from timeit import timeit
from datetime import timedelta
from configparser import ConfigParser

from dlis_writer.file import DLISFile
from dlis_writer.logical_record.collections.frame_data_capsule import FrameDataCapsule
from dlis_writer.logical_record.eflr_types import Frame, Channel
from dlis_writer.utils.loaders import load_hdf5, load_config
from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.utils.make_mock_data_hdf5 import create_data
from dlis_writer.writer.utils.compare_dlis_files import compare


logger = logging.getLogger(__name__)


class DLISWriter:
    default_config_file_name = Path(__file__).resolve().parent/'basic_config.ini',

    def __init__(self, data, config):
        self._data = data
        self._config = config

    @staticmethod
    def make_config(config_file_name, data):
        config = load_config(config_file_name)
        DLISWriter._add_channel_config(data, config=config)
        DLISWriter._add_index_config(config=config, depth_based="Channel-depth" in config.sections())
        return config

    @staticmethod
    def _add_channel_config(data: np.ndarray, config: ConfigParser):
        for name in data.dtype.names:
            section = f"Channel-{name}"
            config.add_section(section)
            config[section]['name'] = name

    @staticmethod
    def _add_index_config(config: ConfigParser, depth_based=False):
        if depth_based:
            config['Frame'].update({'index_type': 'DEPTH', 'spacing.units': 'm'})
        else:
            config['Frame'].update({'index_type': 'TIME', 'spacing.units': 's'})

    @staticmethod
    def create_data(**kwargs):
        return create_data(**kwargs)

    @staticmethod
    def load_data(input_file_name):
        return load_hdf5(input_file_name)

    def make_data_capsule(self, channels: list[Channel] = None) -> FrameDataCapsule:
        frame = Frame.from_config(self._config)

        if channels is None:
            channels = Channel.all_from_config(self._config)
        for channel in channels:
            channel.set_dimension_and_repr_code_from_data(self._data)

        frame.channels.value = channels

        logger.info(f'Preparing frames for {self._data.shape[0]} rows with channels: '
                    f'{", ".join(c.name for c in channels)}')
        data_capsule = FrameDataCapsule(frame, self._data)

        return data_capsule

    def write_dlis_file(self, dlis_file_name, channels=None):
        def timed_func():
            # CREATE THE FILE
            dlis_file = DLISFile.from_config(self._config)

            data_capsule = self.make_data_capsule(channels=channels)

            dlis_file.write_dlis(data_capsule, dlis_file_name)

        exec_time = timeit(timed_func, number=1)
        logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")

    @classmethod
    def make_parser(cls):
        parser = ArgumentParser("DLIS file creation - minimal working example")
        pg = parser.add_mutually_exclusive_group()
        pg.add_argument('-n', '--n-points', help='Number of data points', type=float, default=10e3)
        pg.add_argument('-ifn', '--input-file-name', help='Input file name')

        parser.add_argument('-c', '--config', help="Path to config file specifying metadata")
        parser.add_argument('-fn', '--file-name', help='Output file name')
        parser.add_argument('-ni', '--n-images', type=int, default=0,
                            help='Number of 2D data sets to add (ignored if input file is specified)')
        parser.add_argument('-nc', '--n-cols', type=int, default=128,
                            help='No. columns for each of the added 2D data sets (ignored if input file specified)')
        parser.add_argument('--depth-based', action='store_true', default=False,
                            help="Make a depth-based HDF5 file (default is time-based)")

        return parser

    @classmethod
    def from_parser_args(cls, pargs):
        if (input_file_name := pargs.input_file_name) is None:
            data = cls.create_data(
                n_points=int(pargs.n_points),
                n_images=pargs.n_images,
                n_cols=pargs.n_cols,
                depth_based=pargs.depth_based
            )
        else:
            data = cls.load_data(input_file_name)

        if pargs.config:
            config = load_config(pargs.config)
        else:
            config = cls.make_config(cls.default_config_file_name, data)

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

    dlis_writer = DLISWriter.from_parser_args(pargs)
    dlis_writer.write_dlis_file(dlis_file_name=pargs.output_file_name)

    if pargs.reference_file_name is not None:
        compare_files(pargs.output_file_name, pargs.reference_file_name)
