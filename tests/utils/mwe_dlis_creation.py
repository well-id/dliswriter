from datetime import datetime
from pathlib import Path
import numpy as np
import h5py
import os
from line_profiler_pycharm import profile

from logical_record.file import DLISFile
from logical_record.storage_unit_label import StorageUnitLabel
from logical_record.file_header import FileHeader
from logical_record.origin import Origin
from logical_record.frame import Frame
from logical_record.frame_data import FrameData
from logical_record.utils.enums import Units, RepresentationCode
from logical_record.channel import make_channel
from tests.utils.make_mock_data_hdf5 import create_data


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
    return h5py.File(data_file_name)[f'/{key}/']

@profile
def make_channels_and_frame(data):
    # CHANNELS & FRAME
    frame = Frame('MAIN')
    frame.channels.value = [
        make_channel('posix time', unit='s', data=data['time']),
        make_channel('depth', unit='m', data=data['depth']),
        make_channel('surface rpm', unit='rpm', data=data['rpm']),
    ]

    if 'image' in data.keys():
        frame.channels.value.append(
            make_channel('image', unit='m', data=data['image'].astype(float), dimension=5, element_limit=5)
        )

    frame.index_type.value = 'TIME'
    frame.spacing.representation_code = RepresentationCode.FDOUBL
    frame.spacing.units = Units.s

    # Create FrameData objects
    frame_data_objects = []

    n_points = data["time"].shape[0]
    print(f'Making frames for {n_points} rows.')

    for i in range(n_points):
        slots = np.concatenate([np.stack(v.data[i:i+1]).flatten() for v in frame.channels.value])
        frame_data = FrameData(frame=frame, frame_number=i + 1, slots=slots)
        frame_data_objects.append(frame_data)

    return frame, frame_data_objects

@profile
def write_dlis_file(data, dlis_file_name):
    # CREATE THE FILE
    dlis_file = DLISFile(
        storage_unit_label=StorageUnitLabel(),
        file_header=FileHeader(),
        origin=make_origin()
    )

    frame, frame_data_objects = make_channels_and_frame(data)

    logical_records = [
        *frame.channels.value,
        frame
    ]
    logical_records.extend(frame_data_objects)

    dlis_file.write_dlis(logical_records, dlis_file_name)


if __name__ == '__main__':
    output_file_name = Path(__file__).resolve().parent.parent/'outputs/mwe_fake_dlis'
    os.makedirs(output_file_name.parent, exist_ok=True)

    write_dlis_file(data=create_data(int(10e3)), dlis_file_name=output_file_name)
