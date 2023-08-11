from datetime import datetime
from argparse import ArgumentParser
import numpy as np
import pandas as pd
from pathlib import Path

from logical_record.file import DLISFile
from logical_record.utils.converters import get_representation_code
from logical_record.storage_unit_label import StorageUnitLabel
from logical_record.file_header import FileHeader
from logical_record.origin import Origin
from logical_record.well_reference_point import WellReferencePoint
from logical_record.axis import Axis
from logical_record.channel import Channel
from logical_record.frame import Frame
from logical_record.frame_data import FrameData
from logical_record.utils.enums import Units
from logical_record.utils.enums import RepresentationCode

parser = ArgumentParser()
parser.add_argument("-l", "--length", type=int, help="length", required=True)
parser_args = parser.parse_args()

start = 1275
end = start + parser_args.length

# Read Data
file_path = Path(__name__).resolve().parent / 'data/actual_data.hdf5'
image0 = pd.read_hdf(file_path) * 39.37  # m to inch

depth = np.array(image0.index)
depth = depth.round(2)

depth_start = np.searchsorted(depth, start)
depth_end = np.searchsorted(depth, end)

rows = np.arange(depth_start, depth_end)
# rows = depth

# Convert to numpy.ndarray
image0 = image0.to_numpy()

images = [image0]
max_r = [0] * len(images)
min_r = [0] * len(images)

for i, im in enumerate(images):
    images[i] = np.where(im > 12, np.nan, im)
    max_r[i] = np.nanmax(images[i])
    min_r[i] = np.nanmin(images[i])

# STORAGE UNIT LABEL
sul = StorageUnitLabel()

# FILE HEADER
file_header = FileHeader()

# ORIGIN
origin = Origin('DEFINING ORIGIN')
origin.file_id.value = 'WELL ID'
origin.file_set_name.value = 'WID OSEBERG 30/9-B-45 A T2'
origin.file_set_number.value = 1
origin.file_number.value = 0

origin.creation_time.value = datetime.now()

origin.run_number.value = 1
origin.well_id.value = 0
origin.well_name.value = '30/9-B-45 A T2'
origin.field_name.value = 'OSEBERG'
# origin.producer_code.value = 1
# origin.producer_name.value = 'AQLN producer_name'
origin.company.value = 'Equinor Norway'

# WELL REFERENCE POINT
well_reference_point = WellReferencePoint('WELL-REF')
well_reference_point.permanent_datum.value = 'MSL'
well_reference_point.vertical_zero.value = 'vertical_zero'
well_reference_point.permanent_datum_elevation.value = 0.00
well_reference_point.above_permanent_datum.value = 0.00
well_reference_point.magnetic_declination.value = 0.00

well_reference_point.coordinate_1_name.value = 'Latitude'
well_reference_point.coordinate_1_value.value = 64.93284

well_reference_point.coordinate_2_name.value = 'Longitude'
well_reference_point.coordinate_2_value.value = 2.828584

# AXIS
axis = Axis('AXS-1')
axis.axis_id.value = 'FIRST AXIS'

axis.coordinates.representation_code = RepresentationCode.FDOUBL
axis.coordinates.count = 2
axis.coordinates.value = [59.34211, 1.82791]

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

pad0_channel = Channel('4DCALRITCP0')
pad0_channel.long_name.value = '4DCAL Radii Img TC Pad 0'
pad0_channel.representation_code.value = get_representation_code(RepresentationCode.FDOUBL)
pad0_channel.dimension.value = [128]
pad0_channel.element_limit.value = [128]
pad0_channel.units.value = Units.in_
pad0_channel.minimum_value.value = min_r[0]
pad0_channel.maximum_value.value = max_r[0]

# FRAME
frame = Frame('MAIN')
frame.channels.value = [depth_channel, pad0_channel]
frame.index_type.value = 'BOREHOLE-DEPTH'
frame.spacing.value = 0.01
frame.spacing.representation_code = RepresentationCode.FDOUBL
frame.spacing.units = Units.m

# Create FrameData objects
frame_data_objects = []

print(f'Making frames for {rows.size} rows.')

for i in rows:  # range(len(rows)):

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
    well_reference_point,
    axis,
    depth_channel,
    pad0_channel,
    frame,
]
logical_records.extend(frame_data_objects)

dlis_file.write_dlis(logical_records, './output/test_improved.DLIS')
