from datetime import datetime
from pathlib import Path
import numpy as np
import h5py
import pandas as pd
from line_profiler_pycharm import profile

from file import DLISFile
from logical_record.storage_unit_label import StorageUnitLabel
from logical_record.file_header import FileHeader
from logical_record.origin import Origin
from logical_record.axis import Axis
from logical_record.channel import Channel, make_channel
from logical_record.frame import Frame
from logical_record.frame_data import FrameData
from logical_record.utils.enums import Units
from logical_record.utils.enums import RepresentationCode


# STORAGE UNIT LABEL
sul = StorageUnitLabel()

# FILE HEADER
file_header = FileHeader()

# ORIGIN
origin = Origin('DEFINING ORIGIN')
origin.file_id.value = 'WELL ID'
origin.file_set_name.value = 'WID Tommeliten 1/9-AB-3 H'
origin.file_set_number.value = 1
origin.file_number.value = 0

origin.creation_time.value = datetime.now()

origin.run_number.value = 1
origin.well_id.value = 0
origin.well_name.value = '1/9-AB-3 H'
origin.field_name.value = 'Tommeliten'
origin.company.value = 'ConocoPhillips Skandinavia AS'

# AXIS
axis = Axis('AXS-1')
axis.axis_id.value = 'FIRST AXIS'

axis.spacing.representation_code = RepresentationCode.FDOUBL
axis.spacing.value = 0.01
axis.spacing.units = Units.m

# CHANNEL

# Read Data
data_path = Path(r'C:\Users\kamil.grunwald\AppData\Local\DrillEnlight\0.2\dv')
save_path = Path(r'C:\Users\kamil.grunwald\AppData\Local\DrillEnlight\0.2\dv')

f_down = h5py.File(data_path/'DrillingDynamics_06-Apr-2023.hdf5')['/content/dacq/']
f_surf = h5py.File(data_path/'wellID surface data 1 sec PU to POOH modified for loading.hdf5')

df_down = pd.DataFrame({
    'time': f_down['PosixTime'][0][:][::100],
    'x': f_down['AccelXRawg'][0][:][::100],
    'y': f_down['AccelYRawg'][0][:][::100],
    'z': f_down['AccelZRawg'][0][:][::100],
    'gyro_rpm': f_down['GyroZRaw_rpm'][0][:][::100],
    'rpm': f_down['MagRPM'][0][:][::100],
    'rpm_filtered': f_down['MagFilteredRPM'][0][:][::100]
})

df_surf = pd.DataFrame({
    'time': f_surf['/content/TIME'],
    'rpm': f_surf['/content/FRSA'],
    'depth': f_surf['/content/TFDP'],
    'hole_depth': f_surf['/content/TFMD'],
    'spp': f_surf['/content/FSPA'],
    'torque': f_surf['/content/FTAA'],
    'wob': f_surf['/content/TFBA'],
    'hookload': f_surf['/content/TFHA'],
    'rop': f_surf['/content/ROPA'],
    'flow': f_surf['/content/FFIA'],
    'block': f_surf['/content/BPOS']
})

df_down.index = df_down.time
df_surf.index = df_surf.time
df_down_new = df_down.reindex(df_down.index | df_surf.index).interpolate('index')
df_surf_new = df_surf.reindex(df_down.index | df_surf.index).interpolate('index')
df_down_new.loc[df_down_new.index > 1676818621.920601] = np.nan

# CHANNELS

time_channel = make_channel('posix time', unit='s', data=df_surf_new.time)

depth_channel = make_channel('depth', unit='m', data=df_surf_new.depth)
hole_depth_channel = make_channel('hole depth', unit='m', data=df_surf_new.hole_depth)
rpm_s_channel = make_channel('surface rpm', unit='rpm', data=df_surf_new.rpm)
rpm_mag_channel = make_channel('downhole mag rpm', unit='rpm', data=df_down_new.rpm)
rpm_mag_filter_channel = make_channel('downhole mag rpm (filtered)', unit='rpm', data=df_down_new.rpm_filtered)
rpm_gyro_channel = make_channel('downhole gyro rpm', unit='rpm', data=df_down_new.gyro_rpm)
x_channel = make_channel('x accel', unit='g', data=df_down_new.x)
y_channel = make_channel('y accel', unit='g', data=df_down_new.y)
z_channel = make_channel('z channel', unit='g', data=df_down_new.z)
spp_channel = make_channel('SPP', unit='psi', data=df_surf_new.spp)
torque_channel = make_channel('Torque', unit='kNm', data=df_surf_new.torque)
wob_channel = make_channel('WOB', unit='Tons', data=df_surf_new.wob)
hookload_channel = make_channel('Hookload', unit='Tons', data=df_surf_new.hookload)
rop_channel = make_channel('ROP', unit=r'm/h', data=df_surf_new.rop)
flow_channel = make_channel('Flow In', unit='m3/h', data=df_surf_new.flow)
block_channel = make_channel('Block Position', unit='m', data=df_surf_new.block)


# FRAME
frame = Frame('MAIN')
frame.channels.value = [time_channel,
                        depth_channel,
                        hole_depth_channel,
                        rpm_s_channel,
                        rpm_mag_channel,
                        rpm_mag_filter_channel,
                        rpm_gyro_channel,
                        x_channel,
                        y_channel,
                        z_channel,
                        spp_channel,
                        torque_channel,
                        wob_channel,
                        hookload_channel,
                        rop_channel,
                        flow_channel,
                        block_channel]

frame.index_type.value = 'TIME'
# frame.spacing.value = 0.01
frame.spacing.representation_code = RepresentationCode.FDOUBL
frame.spacing.units = Units.s

# Create FrameData objects
frame_data_objects = []

print(f'Making frames for {df_surf_new.shape[0]} rows.')

for i in range(100000):#df_surf_new.shape[0]):
    slots = np.array([v.data.iloc[i] for v in frame.channels.value])
    frame_data = FrameData(frame=frame, frame_number=i + 1, slots=slots)
    frame_data_objects.append(frame_data)

# REMOVE DATA FROM CHANNELS
for v in frame.channels.value:
    if hasattr(v, 'data'):
        delattr(v, 'data')

# CREATE THE FILE
dlis_file = DLISFile(
    storage_unit_label=sul,
    file_header=file_header,
    origin=origin
)

logical_records = [
    axis,
    *frame.channels.value,
    frame,
]
logical_records.extend(frame_data_objects)

dlis_file.write_dlis(logical_records, save_path/'dynamics_test.DLIS')
