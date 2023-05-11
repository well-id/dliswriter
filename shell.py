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
data_path = Path(r'C:\Users\kamil.grunwald\WELLID\data\Depthmapped SHELL-SHPIRAG-5 run 3\outputs')
depth = np.load(data_path/'depth.npy')
amp = np.load(data_path/'ampc.npy')
drill = np.load(data_path/'drilling_filled.npy')*39.37
pooh = np.load(data_path/'pooh.npy')*39.37
relog = np.load(data_path/'relog.npy')*39.37
rop = np.load(data_path/'rop.npy')
wob = np.load(data_path/'wob.npy')
rpm = np.load(data_path/'rpm.npy')
flow = np.load(data_path/'flow.npy')
rops = np.load(data_path/'rop_s.npy')
wobs = np.load(data_path/'wob_s.npy')
rpms = np.load(data_path/'rpm_s.npy')
flows = np.load(data_path/'flow_s.npy')
gamma = np.load(data_path/'gamma.npy')
res_shallow = np.load(data_path/'res_shal.npy')
res_deep = np.load(data_path/'res_deep.npy')

depth = depth.round(2)

images = [amp, drill, relog, pooh]
max_r = [0] * len(images)
min_r = [0] * len(images)

for i, im in enumerate(images):
    max_r[i] = np.nanmax(images[i])
    min_r[i] = np.nanmin(images[i])

# STORAGE UNIT LABEL
sul = StorageUnitLabel()

# FILE HEADER
file_header = FileHeader()

# ORIGIN
origin = Origin('DEFINING ORIGIN')
origin.file_id.value = 'WELL ID'
origin.file_set_name.value = 'WID SHIPRAG-5'
origin.file_set_number.value = 1
origin.file_number.value = 0

origin.creation_time.value = datetime.now()

origin.run_number.value = 1
origin.well_id.value = 0
origin.well_name.value = 'SHP-5'
origin.field_name.value = 'SHIPRAG'
origin.company.value = 'SHELL ALBANIA'

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

amp_channel = Channel('4DCALRITCP02_AMP')
amp_channel.long_name.value = '4DCAL Amplitude Img Pads 02'
amp_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
amp_channel.dimension.value = [128]
amp_channel.element_limit.value = [128]
# amp_channel.units.value = Units.in_
amp_channel.minimum_value.value = 0
amp_channel.maximum_value.value = 5

drill_channel = Channel('4DCALRITCP0')
drill_channel.long_name.value = '4DCAL Radii Img Pad 0'
drill_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
drill_channel.dimension.value = [128]
drill_channel.element_limit.value = [128]
drill_channel.units.value = Units.in_
drill_channel.minimum_value.value = 16.095120
drill_channel.maximum_value.value = 21.819071

relog_channel = Channel('4DCALRITCP0_RELOG')
relog_channel.long_name.value = '4DCAL Radii Img Pad 0 RELOG'
relog_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
relog_channel.dimension.value = [128]
relog_channel.element_limit.value = [128]
relog_channel.units.value = Units.in_
relog_channel.minimum_value.value = 16.095120
relog_channel.maximum_value.value = 21.819071

pooh_channel = Channel('4DCALRITCP0_POOH')
pooh_channel.long_name.value = '4DCAL Radii Img Pad 0 POOH'
pooh_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
pooh_channel.dimension.value = [128]
pooh_channel.element_limit.value = [128]
pooh_channel.units.value = Units.in_
pooh_channel.minimum_value.value = 16.095120
pooh_channel.maximum_value.value = 21.819071

rpm_channel = Channel('Surface RPM at bit')
rpm_channel.long_name.value = 'RPM'
rpm_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
rpm_channel.units.value = 'rpm'
rpm_channel.dimension.value = [1]
rpm_channel.element_limit.value = [1]

wob_channel = Channel('Surface WOB at bit')
wob_channel.long_name.value = 'WOB'
wob_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
wob_channel.units.value = 'klb'
wob_channel.dimension.value = [1]
wob_channel.element_limit.value = [1]

rop_channel = Channel('Surface ROP at bit')
rop_channel.long_name.value = 'ROP'
rop_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
rop_channel.units.value = 'm/h'
rop_channel.dimension.value = [1]
rop_channel.element_limit.value = [1]

flow_channel = Channel('Surface Flow In at bit')
flow_channel.long_name.value = 'FLOW IN'
flow_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
flow_channel.units.value = 'gpm'
flow_channel.dimension.value = [1]
flow_channel.element_limit.value = [1]

rpms_channel = Channel('Surface RPM at tool')
rpms_channel.long_name.value = 'RPM TOOL'
rpms_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
rpm_channel.units.value = 'rpm'
rpms_channel.dimension.value = [1]
rpms_channel.element_limit.value = [1]

wobs_channel = Channel('Surface WOB at tool')
wobs_channel.long_name.value = 'WOB TOOL'
wobs_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
wobs_channel.units.value = 'klb'
wobs_channel.dimension.value = [1]
wobs_channel.element_limit.value = [1]

rops_channel = Channel('Surface ROP at tool')
rops_channel.long_name.value = 'ROP TOOL'
rops_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
rop_channel.units.value = 'm/h'
rops_channel.dimension.value = [1]
rops_channel.element_limit.value = [1]

flows_channel = Channel('Surface Flow In at tool')
flows_channel.long_name.value = 'FLOW IN TOOL'
flows_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
flows_channel.units.value = 'gpm'
flows_channel.dimension.value = [1]
flows_channel.element_limit.value = [1]

res_channel = Channel('Resistivity Deep')
res_channel.long_name.value = 'RES_DEP'
res_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
res_channel.units.value = 'ohm.m'
res_channel.dimension.value = [1]
res_channel.element_limit.value = [1]

res2_channel = Channel('Resistivity Shallow')
res2_channel.long_name.value = 'RES_SHALL'
res2_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
res2_channel.units.value = 'ohm.m'
res2_channel.dimension.value = [1]
res2_channel.element_limit.value = [1]

gr_channel = Channel('Gamma Ray')
gr_channel.long_name.value = 'GR'
gr_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
gr_channel.units.value = 'API'
gr_channel.dimension.value = [1]
gr_channel.element_limit.value = [1]


# FRAME
frame = Frame('MAIN')
frame.channels.value = [depth_channel, amp_channel, drill_channel, relog_channel, pooh_channel, rpm_channel, rop_channel, wob_channel,
                        flow_channel, rpms_channel, rops_channel, wobs_channel, flows_channel, res_channel, res2_channel,
                        gr_channel]
frame.index_type.value = 'BOREHOLE-DEPTH'
frame.spacing.value = 0.01
frame.spacing.representation_code = RepresentationCode.FDOUBL
frame.spacing.units = Units.m

# Create FrameData objects
frame_data_objects = []

print(f'Making frames for {depth.size} rows.')

for i in range(depth.size-15):
    slots = np.append(np.append(depth[i], [im[i] for im in images]), [rpm[i], rop[i], wob[i], flow[i], rpms[i], rops[i],
                                                                      wobs[i], flows[i], res_deep[i], res_shallow[i],
                                                                      gamma[i]])
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
    amp_channel,
    drill_channel,
    relog_channel,
    pooh_channel,
    rpm_channel,
    rop_channel,
    wob_channel,
    flow_channel,
    rpms_channel,
    rops_channel,
    wobs_channel,
    flows_channel,
    res_channel,
    res2_channel,
    gr_channel,
    frame,
]
logical_records.extend(frame_data_objects)

dlis_file.write_dlis(logical_records, './output/SHELL-SHIPRAG-5 run 3 (revision 4).DLIS')
