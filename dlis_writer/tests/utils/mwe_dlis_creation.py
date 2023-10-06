from datetime import datetime
from pathlib import Path
import numpy as np
import os
import logging
from argparse import ArgumentParser
from timeit import timeit
from datetime import timedelta
from configparser import ConfigParser

from dlis_writer.file import DLISFile, FrameDataCapsule
from dlis_writer.logical_record.misc import StorageUnitLabel, FileHeader
from dlis_writer.logical_record.eflr_types import Origin, Frame, Channel
from dlis_writer.utils.enums import Units, RepresentationCode
from dlis_writer.utils.loaders import load_hdf5
from dlis_writer.utils.logging import install_logger
from dlis_writer.tests.utils.make_mock_data_hdf5 import create_data
from dlis_writer.tests.utils.compare_dlis_files import compare


logger = logging.getLogger(__name__)


def _define_index(frame, depth_based=False):
    rc = RepresentationCode.FDOUBL

    if depth_based:
        logger.debug("Making a depth-based file")
        frame.index_type.value = 'DEPTH'
        frame.spacing.units = Units.s
        index_channel = Channel.create('depth', unit='m', repr_code=rc)
    else:
        logger.debug("Making a time-based file")
        frame.index_type.value = 'TIME'
        frame.spacing.units = Units.m
        index_channel = Channel.create('posix time', unit='s', repr_code=rc, dataset_name='time')

    frame.spacing.representation_code = RepresentationCode.FDOUBL
    return index_channel


def make_channels(data, double_precision=False) -> list[Channel]:
    repr_code = RepresentationCode.FDOUBL if double_precision else RepresentationCode.FSINGL

    channels = [
        Channel.create('surface rpm', unit='rpm', dataset_name='rpm')
    ]

    for name in data.dtype.names:
        if not name.startswith('image'):
            continue

        n_cols = data[name].shape[1]

        channel = Channel.create(
            name,
            dataset_name=name,
            dimension=n_cols,
            element_limit=n_cols,
            unit=Units.in_,
            repr_code=repr_code
        )

        channels.append(channel)

    return channels


def prepare_data(data: np.ndarray, channels: list[Channel], depth_based: bool = False) -> FrameDataCapsule:
    frame = Frame('MAIN')

    index_channel = _define_index(frame, depth_based=depth_based)

    frame.channels.value = [
        index_channel,
        *channels
    ]

    logger.info(f'Preparing frames for {data.shape[0]} rows with channels: '
                f'{", ".join(c.name for c in frame.channels.value)}')
    data_capsule = FrameDataCapsule(frame, data)

    return data_capsule


def write_dlis_file(data, channels, dlis_file_name, config, **kwargs):
    # CREATE THE FILE
    dlis_file = DLISFile(
        storage_unit_label=StorageUnitLabel.from_config(config),
        file_header=FileHeader.from_config(config),
        origin=Origin.from_config(config)
    )

    data_capsule = prepare_data(data, channels, **kwargs)

    dlis_file.write_dlis(data_capsule, dlis_file_name)


if __name__ == '__main__':
    install_logger(logger)

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
    parser.add_argument('-dbl', '--double-precision', action='store_true', default=False,
                        help="Save images in double precision (default: single)")

    pargs = parser.parse_args()

    if (config_file_name := pargs.config) is None:
        config_file_name = Path(__file__).resolve().parent.parent/'resources/mock_config.ini'

    config = ConfigParser()
    config.read(config_file_name)

    if (output_file_name := pargs.file_name) is None:
        output_file_name = Path(__file__).resolve().parent.parent/'outputs/mwe_fake_dlis.DLIS'
        os.makedirs(output_file_name.parent, exist_ok=True)

    if (input_file_name := pargs.input_file_name) is None:
        data = create_data(int(pargs.n_points), n_images=pargs.n_images, n_cols=pargs.n_cols)
    else:
        data = load_hdf5(input_file_name)

    def timed_func():
        channels = make_channels(data, double_precision=pargs.double_precision)

        write_dlis_file(
            data=data,
            channels=channels,
            dlis_file_name=output_file_name,
            depth_based=pargs.depth_based,
            config=config
        )

    exec_time = timeit(timed_func, number=1)
    logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")

    if (reference_file_name := pargs.reference_file_name) is not None:
        logger.info(f"Comparing the newly created DLIS file with a reference file: {reference_file_name}")
        equal = compare(output_file_name, reference_file_name, verbose=True)

        if equal:
            logger.info("Files are equal")
        else:
            logger.warning("Files are NOT equal")

