from pathlib import Path
import numpy as np
import os
import logging
from argparse import ArgumentParser
from timeit import timeit
from datetime import timedelta
from configparser import ConfigParser

from dlis_writer.file import DLISFile, FrameDataCapsule
from dlis_writer.logical_record.eflr_types import Frame, Channel
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.loaders import load_hdf5, load_config
from dlis_writer.utils.logging import install_logger
from dlis_writer.writer.utils.make_mock_data_hdf5 import create_data
from dlis_writer.writer.utils.compare_dlis_files import compare


logger = logging.getLogger(__name__)


def prepare_config(config_fname, data):
    config = load_config(config_fname)
    _add_channel_config(data, config=config)
    _add_index_config(config=config, depth_based="Channel-depth" in config.sections())
    return config


def _add_channel_config(data: np.ndarray, config: ConfigParser,
                        repr_code: RepresentationCode = None):

    for name in data.dtype.names:
        section = f"Channel-{name}"
        config.add_section(section)
        config[section]['name'] = name
        config[section]['dimension'] = ', '.join(str(i) for i in data[name].shape[1:])
        if repr_code:
            config[section]['representation_code'] = str(repr_code.value)


def _add_index_config(config: ConfigParser, depth_based=False):
    if depth_based:
        config['Frame'].update({'index_type': 'DEPTH', 'spacing.units': 'm'})
    else:
        config['Frame'].update({'index_type': 'TIME', 'spacing.units': 's'})


def make_data_capsule(data: np.ndarray, channels: list[Channel], config) -> FrameDataCapsule:
    frame = Frame.from_config(config)
    frame.channels.value = channels

    logger.info(f'Preparing frames for {data.shape[0]} rows with channels: '
                f'{", ".join(c.name for c in frame.channels.value)}')
    data_capsule = FrameDataCapsule(frame, data)

    return data_capsule


def prepare_data_array(pargs):
    if (input_file_name := pargs.input_file_name) is None:
        data = create_data(
            int(pargs.n_points),
            n_images=pargs.n_images,
            n_cols=pargs.n_cols,
            depth_based=pargs.depth_based
        )
    else:
        data = load_hdf5(input_file_name)

    return data


def write_dlis_file(data, channels, dlis_file_name, config):
    def timed_func():
        # CREATE THE FILE
        dlis_file = DLISFile.from_config(config)

        data_capsule = make_data_capsule(data, channels, config=config)

        dlis_file.write_dlis(data_capsule, dlis_file_name)

    exec_time = timeit(timed_func, number=1)
    logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")


def make_parser():
    parser = ArgumentParser("DLIS file creation - minimal working example")
    pg = parser.add_mutually_exclusive_group()
    pg.add_argument('-n', '--n-points', help='Number of data points', type=float, default=10e3)
    pg.add_argument('-ifn', '--input-file-name', help='Input file name')

    parser.add_argument('-c', '--config', help="Path to config file specifying metadata")
    parser.add_argument('-fn', '--file-name', help='Output file name')
    parser.add_argument('-ref', '--reference-file-name',
                        help="Another DLIS file to compare the created one against (at binary level)")
    parser.add_argument('-ni', '--n-images', type=int, default=0,
                        help='Number of 2D data sets to add (ignored if input file is specified)')
    parser.add_argument('-nc', '--n-cols', type=int, default=128,
                        help='Number of columns for each of the added 2D data sets (ignored if input file specified)')
    parser.add_argument('--depth-based', action='store_true', default=False,
                        help="Make a depth-based HDF5 file (default is time-based)")

    return parser


def compare_files(output_file_name, reference_file_name):
    logger.info(f"Comparing the newly created DLIS file with a reference file: {reference_file_name}")
    equal = compare(output_file_name, reference_file_name, verbose=True)
    if equal:
        logger.info("Files are equal")
    else:
        logger.warning("Files are NOT equal")


if __name__ == '__main__':
    install_logger(logger)

    parser = make_parser()
    parser.set_defaults(
        config_file_name=Path(__file__).resolve().parent/'mwe_mock_config.ini',
        output_file_name=Path(__file__).resolve().parent.parent/'tests/outputs/mwe_fake_dlis.DLIS'
    )
    pargs = parser.parse_args()

    data = prepare_data_array(pargs)
    cfg = prepare_config(pargs.config_file_name, data=data)

    channels = Channel.all_from_config(cfg)

    write_dlis_file(data=data, channels=channels, dlis_file_name=pargs.output_file_name, config=cfg)

    if pargs.reference_file_name is not None:
        compare_files(pargs.output_file_name, pargs.reference_file_name)

