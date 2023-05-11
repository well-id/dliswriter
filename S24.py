from datetime import datetime
from pathlib import Path
import numpy as np

from file import DLISFile
from logical_record.utils.converters import get_representation_code
from logical_record.storage_unit_label import StorageUnitLabel
from logical_record.file_header import FileHeader
from logical_record.origin import Origin
from logical_record.axis import Axis
from logical_record.channel import Channel
from logical_record.frame import Frame
from logical_record.frame_data import FrameData
from logical_record.utils.enums import Units
from logical_record.utils.enums import RepresentationCode

# Read Data
data_path = Path(r'C:\Users\kamil.grunwald\WELLID\data\24-A\images')
save_path = Path(r'C:\Users\kamil.grunwald\WELLID\data\24-A\dlis')
depth = np.load(data_path/'depth.npy') + 41.89
ampc = np.load(data_path/'ac.npy')
drillc = np.load(data_path/'rc.npy')*39.37 - 0.625
amp_pooh = np.load(data_path/'ac_pooh1.npy')
pooh = np.load(data_path/'rc_pooh1.npy')*39.37 - 0.625
amp_pooh2 = np.load(data_path/'ac_pooh2.npy')
pooh2 = np.load(data_path/'rc_pooh2.npy')*39.37 - 0.625

r_drill = np.array([np.sqrt(np.sum(drillc[i]**2) / 128) for i in range(len(drillc))])*2
r_pooh1 = np.array([np.sqrt(np.sum(pooh[i]**2) / 128) for i in range(len(pooh))])*2
r_pooh2 = np.array([np.sqrt(np.sum(pooh2[i]**2) / 128) for i in range(len(pooh2))])*2


images = [ampc, drillc, amp_pooh, pooh, amp_pooh2, pooh2]
max_r = [0] * len(images)
min_r = [0] * len(images)

# STORAGE UNIT LABEL
sul = StorageUnitLabel()

# FILE HEADER
file_header = FileHeader()

# ORIGIN
origin = Origin('DEFINING ORIGIN')
origin.file_id.value = 'WELL ID'
origin.file_set_name.value = 'WID Ost Frigg 25/2-24 A'
origin.file_set_number.value = 1
origin.file_number.value = 0

origin.creation_time.value = datetime.now()

origin.run_number.value = 1
origin.well_id.value = 0
origin.well_name.value = '25/2-24 A'
origin.field_name.value = 'Ost Frigg'
origin.company.value = 'AkerBP'

# AXIS
axis = Axis('AXS-1')
axis.axis_id.value = 'FIRST AXIS'

axis.spacing.representation_code = RepresentationCode.FDOUBL
axis.spacing.value = 0.01
axis.spacing.units = Units.m

# CHANNEL

# For each column create a Channel object defining properties of that column
depth_channel = Channel('DEPTH CHANNEL')
depth_channel.long_name.value = 'DEPTH'
depth_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
depth_channel.units.value = Units.m
depth_channel.dimension.value = [1]
depth_channel.element_limit.value = [1]

ampc_channel = Channel('4DCALRITCP_ALL_AMP')
ampc_channel.long_name.value = '4DCAL Amplitude Img Pads ALL'
ampc_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
ampc_channel.dimension.value = [128]
ampc_channel.element_limit.value = [128]
ampc_channel.minimum_value.value = 0
ampc_channel.maximum_value.value = 10

drillc_channel = Channel('4DCALRITCP_ALL')
drillc_channel.long_name.value = '4DCAL Radii Img Pads ALL'
drillc_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
drillc_channel.dimension.value = [128]
drillc_channel.element_limit.value = [128]
drillc_channel.units.value = Units.in_
drillc_channel.minimum_value.value = 5
drillc_channel.maximum_value.value = 8.6

pooh_amp_channel = Channel('4DCALRITCP_ALL_POOH_AMP')
pooh_amp_channel.long_name.value = '4DCAL Amplitude Img Pads ALL POOH'
pooh_amp_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
pooh_amp_channel.dimension.value = [128]
pooh_amp_channel.element_limit.value = [128]
pooh_amp_channel.minimum_value.value = 0
pooh_amp_channel.maximum_value.value = 10

pooh_channel = Channel('4DCALRITCP_ALL_POOH')
pooh_channel.long_name.value = '4DCAL Radii Img Pads ALL POOH'
pooh_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
pooh_channel.dimension.value = [128]
pooh_channel.element_limit.value = [128]
pooh_channel.units.value = Units.in_
pooh_channel.minimum_value.value = 5
pooh_channel.maximum_value.value = 8.6

pooh2_amp_channel = Channel('4DCALRITCP_ALL_POOH2_AMP')
pooh2_amp_channel.long_name.value = '4DCAL Amplitude Img Pads ALL POOH2'
pooh2_amp_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
pooh2_amp_channel.dimension.value = [128]
pooh2_amp_channel.element_limit.value = [128]
pooh2_amp_channel.minimum_value.value = 0
pooh2_amp_channel.maximum_value.value = 10

pooh2_channel = Channel('4DCALRITCP_POOH2_ALL')
pooh2_channel.long_name.value = '4DCAL Radii Img Pads ALL POOH2'
pooh2_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
pooh2_channel.dimension.value = [128]
pooh2_channel.element_limit.value = [128]
pooh2_channel.units.value = Units.in_
pooh2_channel.minimum_value.value = 5
pooh2_channel.maximum_value.value = 8.6

r_drill_channel = Channel('AREA EQUIVALENT DIAMETER DRILLING')
r_drill_channel.long_name.value = 'AREA EQUIVALENT DIAMETER'
r_drill_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
r_drill_channel.units.value = Units.in_
r_drill_channel.dimension.value = [1]
r_drill_channel.element_limit.value = [1]

r_pooh1_channel = Channel('AREA EQUIVALENT DIAMETER POOH1')
r_pooh1_channel.long_name.value = 'AREA EQUIVALENT DIAMETER'
r_pooh1_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
r_pooh1_channel.units.value = Units.in_
r_pooh1_channel.dimension.value = [1]
r_pooh1_channel.element_limit.value = [1]

r_pooh2_channel = Channel('AREA EQUIVALENT DIAMETER POOH2')
r_pooh2_channel.long_name.value = 'AREA EQUIVALENT DIAMETER'
r_pooh2_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
r_pooh2_channel.units.value = Units.in_
r_pooh2_channel.dimension.value = [1]
r_pooh2_channel.element_limit.value = [1]

# FRAME
frame = Frame('MAIN')
frame.channels.value = [depth_channel, ampc_channel, drillc_channel, pooh_amp_channel,
                        pooh_channel, pooh2_amp_channel, pooh2_channel, r_drill_channel,
                        r_pooh1_channel, r_pooh2_channel]
frame.index_type.value = 'BOREHOLE-DEPTH'
frame.spacing.value = 0.01
frame.spacing.representation_code = RepresentationCode.FDOUBL
frame.spacing.units = Units.m

# Create FrameData objects
frame_data_objects = []

print(f'Making frames for {depth.size} rows.')

for i in range(depth.size):
    slots = np.append(np.append(depth[i], [im[i] for im in images]), [r_drill[i], r_pooh1[i], r_pooh2[i]])

    frame_data = FrameData(frame=frame, frame_number=i + 1, slots=slots)
    frame_data_objects.append(frame_data)

# CREATE THE FILE
dlis_file = DLISFile(
    storage_unit_label=sul,
    file_header=file_header,
    origin=origin
)

logical_records = [
    axis,
    depth_channel,
    ampc_channel,
    drillc_channel,
    pooh_amp_channel,
    pooh_channel,
    pooh2_amp_channel,
    pooh2_channel,
    r_drill_channel,
    r_pooh1_channel,
    r_pooh2_channel,
    frame,
]
logical_records.extend(frame_data_objects)

dlis_file.write_dlis(logical_records, save_path/'AkerBP Ost Frigg 25-2-24 A (rev 5).DLIS')
