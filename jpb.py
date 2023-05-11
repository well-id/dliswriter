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
data_path = Path(r"C:\Users\kamil.grunwald\WELLID\data\Osberg B-45\4460m - 4846m")
data = np.load(data_path/'depth.npy')
# inc = np.load(data_path/'inc.npy')

# r0 = np.load(data_path/'r0.npy')
# r1 = np.load(data_path/'r1.npy')
# r2 = np.load(data_path/'r2.npy')
# r3 = np.load(data_path/'r3.npy')
rc = np.load(data_path/'rc.npy')
ac = np.load(data_path/'ac.npy')
# a0 = np.load(data_path/'a0.npy')
# a1 = np.load(data_path/'a1.npy')
# a2 = np.load(data_path/'a2.npy')
# a3 = np.load(data_path/'a3.npy')
# image0 = r0 * 39.3701  # m to inch
# image1 = r1 * 39.3701  # m to inch
# image2 = r2 * 39.3701  # m to inch
# image3 = r3 * 39.3701  # m to inch
imagec = rc * 39.3701  # m to inch

# multi_r = np.array([image0[:, i] + image0[:, 64+i] for i in [n*8 for n in range(8)]])

depth = data
# depth = depth.round(2)

images = [ac, imagec]#, image0, a0, image1, a1, image2, a2, image3, a3]


# STORAGE UNIT LABEL
sul = StorageUnitLabel()

# FILE HEADER
file_header = FileHeader()

# ORIGIN
origin = Origin('DEFINING ORIGIN')
origin.file_id.value = 'WELL ID'
origin.file_set_name.value = 'WID OSEBERG B-45'
origin.file_set_number.value = 1
origin.file_number.value = 0

origin.creation_time.value = datetime.now()

origin.run_number.value = 1
origin.well_id.value = 0
origin.well_name.value = '30/9 B-45'
origin.field_name.value = 'Oseberg'
origin.company.value = 'Equinor Norway'

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

# inc_channel = Channel('INCLINATION CHANNEL')
# inc_channel.long_name.value = 'INC'
# inc_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# inc_channel.units.value = Units.deg
# inc_channel.dimension.value = [1]
# inc_channel.element_limit.value = [1]

padc_channel = Channel('4DCALRITCP_ALL')
padc_channel.long_name.value = '4DCAL Radii Img TC All Pads'
padc_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
padc_channel.dimension.value = [128]
padc_channel.element_limit.value = [128]
padc_channel.units.value = Units.in_
padc_channel.minimum_value.value = 5
padc_channel.maximum_value.value = 8

ampc_channel = Channel('4DCALRITCP_AMP_ALL')
ampc_channel.long_name.value = '4DCAL Amplitude Img All Pads'
ampc_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
ampc_channel.dimension.value = [128]
ampc_channel.element_limit.value = [128]
ampc_channel.minimum_value.value = 0
ampc_channel.maximum_value.value = 15

# pad0_channel = Channel('4DCALRITCP0')
# pad0_channel.long_name.value = '4DCAL Radii Img TC Pad 0'
# pad0_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# pad0_channel.dimension.value = [128]
# pad0_channel.element_limit.value = [128]
# pad0_channel.units.value = Units.in_
# pad0_channel.minimum_value.value = 5.9
# pad0_channel.maximum_value.value = 11.1
#
# amp0_channel = Channel('4DCALRITCP_AMP_0')
# amp0_channel.long_name.value = '4DCAL Amplitude Img Pad 0'
# amp0_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# amp0_channel.dimension.value = [128]
# amp0_channel.element_limit.value = [128]
# # ampc_channel.units.value = Units.A
# amp0_channel.minimum_value.value = 5
# amp0_channel.maximum_value.value = 25
#
# pad1_channel = Channel('4DCALRITCP1')
# pad1_channel.long_name.value = '4DCAL Radii Img TC Pad 1'
# pad1_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# pad1_channel.dimension.value = [128]
# pad1_channel.element_limit.value = [128]
# pad1_channel.units.value = Units.in_
# pad1_channel.minimum_value.value = 5.9
# pad1_channel.maximum_value.value = 11.1
#
# amp1_channel = Channel('4DCALRITCP_AMP_1')
# amp1_channel.long_name.value = '4DCAL Amplitude Img Pad 1'
# amp1_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# amp1_channel.dimension.value = [128]
# amp1_channel.element_limit.value = [128]
# # ampc_channel.units.value = Units.A
# amp1_channel.minimum_value.value = 5
# amp1_channel.maximum_value.value = 25
#
# pad2_channel = Channel('4DCALRITCP2')
# pad2_channel.long_name.value = '4DCAL Radii Img TC Pad 2'
# pad2_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# pad2_channel.dimension.value = [128]
# pad2_channel.element_limit.value = [128]
# pad2_channel.units.value = Units.in_
# pad2_channel.minimum_value.value = 5.9
# pad2_channel.maximum_value.value = 11.1
#
# amp2_channel = Channel('4DCALRITCP_AMP_2')
# amp2_channel.long_name.value = '4DCAL Amplitude Img Pad 2'
# amp2_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# amp2_channel.dimension.value = [128]
# amp2_channel.element_limit.value = [128]
# # ampc_channel.units.value = Units.A
# amp2_channel.minimum_value.value = 5
# amp2_channel.maximum_value.value = 25
#
# pad3_channel = Channel('4DCALRITCP3')
# pad3_channel.long_name.value = '4DCAL Radii Img TC Pad 3'
# pad3_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# pad3_channel.dimension.value = [128]
# pad3_channel.element_limit.value = [128]
# pad3_channel.units.value = Units.in_
# pad3_channel.minimum_value.value = 5.9
# pad3_channel.maximum_value.value = 11.1
#
# amp3_channel = Channel('4DCALRITCP_AMP_3')
# amp3_channel.long_name.value = '4DCAL Amplitude Img Pad 3'
# amp3_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# amp3_channel.dimension.value = [128]
# amp3_channel.element_limit.value = [128]
# # amp3_channel.units.value = Units.A
# amp3_channel.minimum_value.value = 5
# amp3_channel.maximum_value.value = 25
#
# multi_dim_channel = Channel('8-TRACK DIAMETER')
# multi_dim_channel.long_name.value = '8-TRACK DIAMETER'
# multi_dim_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
# multi_dim_channel.units.value = Units.in_
# multi_dim_channel.dimension.value = [8]
# multi_dim_channel.element_limit.value = [8]

# FRAME
frame = Frame('MAIN')
frame.channels.value = [depth_channel, ampc_channel, padc_channel]
                        # pad0_channel, amp0_channel,
                        # pad1_channel, amp1_channel, pad2_channel, amp2_channel, pad3_channel, amp3_channel, multi_dim_channel]
frame.index_type.value = 'BOREHOLE-DEPTH'
frame.spacing.value = 0.01
frame.spacing.representation_code = RepresentationCode.FDOUBL
frame.spacing.units = Units.m

# Create FrameData objects
frame_data_objects = []

print(f'Making frames for {depth.size} rows.')

for i in range(0, depth.size):
    slots = np.append(depth[i], [im[i] for im in images])
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
    padc_channel,
    # pad0_channel,
    # amp0_channel,
    # pad1_channel,
    # amp1_channel,
    # pad2_channel,
    # amp2_channel,
    # pad3_channel,
    # amp3_channel,
    # multi_dim_channel,
    frame,
]
logical_records.extend(frame_data_objects)

dlis_file.write_dlis(logical_records, './output/Oseberg B-45 12.25 inch (4460m - 4846m).DLIS')
