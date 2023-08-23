from datetime import datetime
from pathlib import Path
import numpy as np
import h5py
import os
import logging
from line_profiler_pycharm import profile

from dlis_writer.file.file import DLISFile
from dlis_writer.logical_record.misc.storage_unit_label import StorageUnitLabel
from dlis_writer.logical_record.misc.file_header import FileHeader
from dlis_writer.logical_record.eflr_types.origin import Origin
from dlis_writer.logical_record.eflr_types.frame import Frame
from dlis_writer.logical_record.iflr_types.multi_frame_data import MultiFrameData
from dlis_writer.utils.enums import Units, RepresentationCode
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.tests.utils.make_mock_data_hdf5 import create_data


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


def load_h5_data(data_file_name, key='contents'):
    h5_data = h5py.File(data_file_name, 'r')[f'/{key}/']

    dtype = []
    arrays = []
    n_rows = None
    for key in h5_data.keys():
        key_data = h5_data.get(key)[:]
        arrays.append(key_data)

        dt = (key, key_data.dtype)
        if key_data.ndim > 1:
            dt = (*dt, key_data.shape[-1])
        dtype.append(dt)

        if n_rows is None:
            n_rows = key_data.shape[0]
        else:
            if n_rows != key_data.shape[0]:
                raise RuntimeError(
                    "Datasets in the file have different lengths; the data cannot be transformed to DLIS format")

    full_data = np.zeros(n_rows, dtype=dtype)
    for key, arr in zip(h5_data.keys(), arrays):
        full_data[key] = arr

    return full_data


@profile
def make_channels_and_frame(data: np.ndarray):
    # CHANNELS & FRAME
    frame = Frame('MAIN')
    frame.channels.value = [
        Channel.create('posix time', unit='s', data=data['time']),
        Channel.create('depth', unit='m', data=data['depth']),
        Channel.create('surface rpm', unit='rpm', data=data['rpm']),
    ]

    channel_name_mapping = {'posix time': 'time', 'depth': 'depth', 'surface rpm': 'rpm'}

    if 'image' in data.dtype.names:
        n_cols = data['image'].shape[-1]
        frame.channels.value.append(
            Channel.create('image', unit='m', data=data['image'], dimension=n_cols, element_limit=n_cols)
        )
        channel_name_mapping['image'] = 'image'

    frame.index_type.value = 'TIME'
    frame.spacing.representation_code = RepresentationCode.FDOUBL
    frame.spacing.units = Units.s

    n_points = data.shape[0]
    logger.info(f'Preparing frames for {n_points} rows.')
    multi_frame_data = MultiFrameData(frame, data, channel_name_mapping=channel_name_mapping)

    return frame, multi_frame_data

@profile
def write_dlis_file(data, dlis_file_name):
    # CREATE THE FILE
    dlis_file = DLISFile(
        storage_unit_label=StorageUnitLabel(),
        file_header=FileHeader(),
        origin=make_origin()
    )

    frame, data_logical_records = make_channels_and_frame(data)

    meta_logical_records = [
        *frame.channels.value,
        frame
    ]

    dlis_file.write_dlis(meta_logical_records, data_logical_records, dlis_file_name)


if __name__ == '__main__':
    output_file_name = Path(__file__).resolve().parent.parent/'outputs/mwe_fake_dlis.DLIS'
    os.makedirs(output_file_name.parent, exist_ok=True)

    write_dlis_file(data=create_data(int(10e3), add_2d=True), dlis_file_name=output_file_name)
