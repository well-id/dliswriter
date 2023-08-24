from datetime import datetime
from pathlib import Path
import numpy as np
import os
import logging
from argparse import ArgumentParser
from timeit import timeit
from datetime import timedelta
from line_profiler_pycharm import profile

from dlis_writer.file import DLISFile, FrameDataCapsule
from dlis_writer.logical_record.misc import StorageUnitLabel, FileHeader
from dlis_writer.logical_record.eflr_types import Origin, Frame, Channel
from dlis_writer.utils.enums import Units, RepresentationCode
from dlis_writer.utils.loaders import load_hdf5
from dlis_writer.utils.logging import install_logger
from dlis_writer.tests.utils.make_mock_data_hdf5 import create_data
from dlis_writer.tests.utils.compare_dlis_files import compare


logger = logging.getLogger(__name__)


def make_origin():
    # ORIGIN
    origin = Origin('DEFINING ORIGIN')
    origin.file_id.value = 'WELL ID'
    origin.file_set_name.value = 'Test file set name'
    origin.file_set_number.value = 1
    origin.file_number.value = 0

    origin.creation_time.value = datetime(year=2050, month=3, day=2, hour=15, minute=30)

    origin.run_number.value = 1
    origin.well_id.value = 0
    origin.well_name.value = 'Test well name'
    origin.field_name.value = 'Test field name'
    origin.company.value = 'Test company'

    return origin


def make_channels_and_frame(data: np.ndarray) -> FrameDataCapsule:
    # CHANNELS & FRAME
    frame = Frame('MAIN')
    frame.channels.value = [
        Channel.create('posix time', unit='s', dataset_name='time'),
        Channel.create('depth', unit='m'),
        Channel.create('surface rpm', unit='rpm', dataset_name='rpm'),
    ]

    if 'image' in data.dtype.names:
        n_cols = data['image'].shape[-1]
        frame.channels.value.append(
            Channel.create('image', unit='m', dimension=n_cols, element_limit=n_cols)
        )

    frame.index_type.value = 'TIME'
    frame.spacing.representation_code = RepresentationCode.FDOUBL
    frame.spacing.units = Units.s

    logger.info(f'Preparing frames for {data.shape[0]} rows.')
    data_capsule = FrameDataCapsule(frame, data)

    return data_capsule


@profile
def write_dlis_file(data, dlis_file_name):
    # CREATE THE FILE
    dlis_file = DLISFile(
        storage_unit_label=StorageUnitLabel(),
        file_header=FileHeader(),
        origin=make_origin()
    )

    data_capsule = make_channels_and_frame(data)

    dlis_file.write_dlis(data_capsule, dlis_file_name)


if __name__ == '__main__':
    install_logger(logger)

    parser = ArgumentParser("DLIS file creation - minimal working example")
    pg = parser.add_mutually_exclusive_group()
    pg.add_argument('-n', '--n-points', help='Number of data points', type=float, default=10e3)
    pg.add_argument('-ifn', '--input-file-name', help='Input file name')

    parser.add_argument('-fn', '--file-name', help='Output file name')
    parser.add_argument('-ref', '--reference-file-name',
                        help="Another DLIS file to compare the created one against (at binary level)")
    parser.add_argument('--image-cols', nargs='+', type=int, default=(),
                        help='Add 2D data entries with specified numbers of columns '
                             '(ignored if input file name is specified)')

    pargs = parser.parse_args()

    if (output_file_name := pargs.file_name) is None:
        output_file_name = Path(__file__).resolve().parent.parent/'outputs/mwe_fake_dlis.DLIS'
        os.makedirs(output_file_name.parent, exist_ok=True)

    if (input_file_name := pargs.input_file_name) is None:
        data = create_data(int(pargs.n_points), image_cols=pargs.image_cols)
    else:
        data = load_hdf5(input_file_name)

    exec_time = timeit(lambda: write_dlis_file(data=data, dlis_file_name=output_file_name), number=1)
    logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")

    if (reference_file_name := pargs.reference_file_name) is not None:
        logger.info(f"Comparing the newly created DLIS file with a reference file: {reference_file_name}")
        equal = compare(output_file_name, reference_file_name, verbose=True)

        if equal:
            logger.info("Files are equal")
        else:
            logger.warning("Files are NOT equal")

