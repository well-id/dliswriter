from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

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
n_points = int(3e4)
df_surf = pd.DataFrame({
    'time': np.arange(n_points),
    'depth': 10 * (np.arange(n_points) % 5),
    'rpm': 10 * np.sin(np.linspace(0, 1e4*np.pi, n_points)),
})

df_surf.index = df_surf.time

# CHANNELS & FRAME
frame = Frame('MAIN')
frame.channels.value = [
    make_channel('posix time', unit='s', data=df_surf.time),
    make_channel('depth', unit='m', data=df_surf.depth),
    make_channel('surface rpm', unit='rpm', data=df_surf.rpm),
]

frame.index_type.value = 'TIME'
frame.spacing.representation_code = RepresentationCode.FDOUBL
frame.spacing.units = Units.s

# Create FrameData objects
frame_data_objects = []

print(f'Making frames for {df_surf.shape[0]} rows.')

for i in range(df_surf.shape[0]):
    slots = np.array([v.data.iloc[i] for v in frame.channels.value])
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

save_path = Path(__file__).resolve().parent/'outputs'
dlis_file.write_dlis(logical_records, save_path/'mwe_fake_dlis.DLIS')
