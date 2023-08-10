from datetime import datetime
from pathlib import Path
import numpy as np
import h5py

from file import DLISFile
from logical_record.storage_unit_label import StorageUnitLabel
from logical_record.file_header import FileHeader
from logical_record.origin import Origin
from logical_record.frame import Frame
from logical_record.frame_data import FrameData
from logical_record.utils.enums import Units, RepresentationCode
from logical_record.channel import make_channel


# ORIGIN
origin = Origin('DEFINING ORIGIN')
origin.file_id.value = 'WELL ID'
origin.file_set_name.value = 'Test file set name'
origin.file_set_number.value = 1
origin.file_number.value = 0

origin.creation_time.value = datetime.now()

origin.run_number.value = 1
origin.well_id.value = 0
origin.well_name.value = 'Test well name'
origin.field_name.value = 'Test field name'
origin.company.value = 'Test company'


# DATA (fake)
base_data_path = Path(__file__).resolve().parent.parent
data = h5py.File(base_data_path/'resources/mock_data.hdf5')['/contents/']

# CHANNELS & FRAME
frame = Frame('MAIN')
frame.channels.value = [
    make_channel('posix time', unit='s', data=data['time']),
    make_channel('depth', unit='m', data=data['depth']),
    make_channel('surface rpm', unit='rpm', data=data['rpm']),
]

frame.index_type.value = 'TIME'
frame.spacing.representation_code = RepresentationCode.FDOUBL
frame.spacing.units = Units.s

# Create FrameData objects
frame_data_objects = []

n_points = data["time"].shape[0]
print(f'Making frames for {n_points} rows.')

for i in range(n_points):
    slots = np.array([v.data[i] for v in frame.channels.value])
    frame_data = FrameData(frame=frame, frame_number=i + 1, slots=slots)
    frame_data_objects.append(frame_data)

# CREATE THE FILE
dlis_file = DLISFile(
    storage_unit_label=StorageUnitLabel(),
    file_header=FileHeader(),
    origin=origin
)

logical_records = [
    *frame.channels.value,
    frame
]
logical_records.extend(frame_data_objects)

save_path = base_data_path/'outputs'
dlis_file.write_dlis(logical_records, save_path/'mwe_fake_dlis.DLIS')
