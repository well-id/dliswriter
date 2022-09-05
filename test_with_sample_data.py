from datetime import datetime
import io

from storage_unit_label import StorageUnitLabel

from visible_record import VisibleRecord

from logical_record import FileHeader
from logical_record import Origin
from logical_record import WellReferencePoint
from logical_record import Channel
from logical_record import ChannelLogicalRecord
from logical_record import Frame
from logical_record import FrameData
from logical_record import EOD

from common.data_types import struct_type_dict
from common.data_types import read_struct
from common.data_types import write_struct

from utils.converters import get_datetime


import pandas as pd
import numpy as np

from dlisio import dlis





# ORIGIN

origin = Origin()

origin.file_id = 'AQLN file_id'
origin.file_set_name = 'AQLN file_set_name'
origin.file_set_number = 11
origin.file_number = 22
origin.file_type = 'AQLN file_type'
origin.product = 'AQLN product'
origin.version = 'AQLN version'
origin.programs = 'AQLN programs'
# origin.creation_time = datetime.now()
origin.order_number = 'AQLN order_number'
origin.descent_number = 33
origin.run_number = 44
origin.well_id = 55
origin.well_name = 'AQLN well_name'
origin.field_name = 'AQLN field_name'
origin.producer_code = 1
origin.producer_name = 'AQLN producer_name'
origin.company = 'AQLN company'
origin.name_space_name = 'AQLN name_space_name'
origin.name_space_version = 66

origin.origin_reference = origin.file_set_number
origin.object_name = 'DEFINING ORIGIN'
origin.set_name = 'OGR SET NAME'


# FILE-HEADER
file_header = FileHeader()
file_header.origin_reference = origin.file_set_number




# WELL-REFERENCE-POINT

well_reference_point = WellReferencePoint()

well_reference_point.permanent_datum = 'AQLN permanent_datum'
well_reference_point.vertical_zero = 'AQLN vertical_zero'
well_reference_point.permanent_datum_elevation = 1234.51
well_reference_point.above_permanent_datum = 888.51
well_reference_point.magnetic_declination = 999.51
well_reference_point.coordinate_1_name = 'Lattitude'
well_reference_point.coordinate_1_value = 40.395240
well_reference_point.coordinate_2_name = 'Longitude'
well_reference_point.coordinate_2_value = 27.792470

well_reference_point.origin_reference = origin.file_set_number
well_reference_point.object_name = 'AQLN WELL-REF'
well_reference_point.set_name = 'WELL-REF-SET-NAME'



# Read Data
data = pd.read_csv('./data/data.csv')

# Remove index col if exists 
data = data[[col for col in data.columns[1:]]]

# Convert to numpy.ndarray
data = data.values[-40:]



# For each column create a Channel object defining properties of that column

depth_channel = Channel()
depth_channel.long_name = 'DEPTH'
depth_channel.properties = ['0309 AQLN PROP 1', 'PROP AQLN 2']
depth_channel.representation_code = 'FDOUBL'
depth_channel.units = 'm'
depth_channel.dimension = [1]
depth_channel.element_limit = [1]

depth_channel.origin_reference = origin.file_set_number
depth_channel.object_name = 'DEPTH CHANNEL'



curve_1_channel = Channel()
curve_1_channel.long_name = 'CURVE 1'
curve_1_channel.representation_code = 'FDOUBL'
curve_1_channel.units = 't'
curve_1_channel.dimension = [1]
curve_1_channel.element_limit = [1]

curve_1_channel.origin_reference = origin.file_set_number
curve_1_channel.object_name = 'CURVE 1 CHANNEL'




curve_2_channel = Channel()
curve_2_channel.long_name = 'CURVE 2'
curve_2_channel.representation_code = 'FDOUBL'
curve_2_channel.units = 't'
curve_2_channel.dimension = [1]
curve_2_channel.element_limit = [1]
curve_2_channel.origin_reference = origin.file_set_number
curve_2_channel.object_name = 'CURVE 2 CHANNEL'


# Now create a CHANNEL Logical Record object

channel_logical_record = ChannelLogicalRecord()
channel_logical_record.channels = [depth_channel, curve_1_channel, curve_2_channel]

channel_logical_record.origin_reference = origin.file_set_number
channel_logical_record.object_name = 'CHANNEL EFLR'


# Create a FRAME
frame = Frame()
frame.channels = [depth_channel, curve_1_channel, curve_2_channel]
frame.index_type = 'BOREHOLE-DEPTH'
frame.spacing = 0.33
frame.spacing_units = 'm'

frame.origin_reference = origin.file_set_number
frame.object_name = 'MAIN'


# Create FrameData objects

frame_data_objects = []

for i in range(len(data)):
	frame_data = FrameData(frame=frame, frame_number=i+1, slots=data[i])
	frame_data_objects.append(frame_data)




# STORAGE-UNIT-LABEL
sul = StorageUnitLabel()

# VISIBLE-RECORD
visible_record = VisibleRecord()

visible_record.logical_record_segments.append(file_header)
visible_record.logical_record_segments.append(origin)
visible_record.logical_record_segments.append(well_reference_point)
visible_record.logical_record_segments.append(channel_logical_record)
visible_record.logical_record_segments.append(frame)

for frame_data in frame_data_objects:
	visible_record.logical_record_segments.append(frame_data)

dlis_bytes = sul.get_as_bytes() + visible_record.get_as_bytes()
file_name = 'test_with_curves_22.DLIS'

with open(file_name, 'wb') as f:
	f.write(dlis_bytes)


print(f'DLIS file {file_name} is created..')

print('Reading file with dlisio')
with dlis.load(file_name) as (f, *tail):
    print(f.describe())
    print('\n')
    print(f.fileheader.describe())
    print('\n')
    print(f.origins[0].describe())

print('\n\ndone..')









# WRITE AS CSV USING DLISPY
print('Dump using dlispy, to folder named "output22"')
from dlispy import dump
dump(file_name, output_path='output22', eflr_only= False)
print('\ndone..\n\n')