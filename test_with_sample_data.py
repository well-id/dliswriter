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
from logical_record import Zone
from logical_record import Parameter
from logical_record import ParameterLogicalRecord
from logical_record import Equipment

from common.data_types import struct_type_dict
from common.data_types import read_struct
from common.data_types import write_struct


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
origin.creation_time = datetime.now()
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



# ZONE

zone_1 = Zone()
zone_1.description = 'DEPTH ZONE'
zone_1.domain = 'BOREHOLE-DEPTH'
zone_1.maximum = 922.98
zone_1.minimum = 10.42
zone_1.units = 'm'

zone_1.origin_reference = origin.file_set_number
zone_1.object_name = 'DEPTH ZONE OBJ'


zone_2 = Zone()
zone_2.description = 'TIME'
zone_2.domain = 'TIME'
zone_2.minimum = datetime(2022, 8, 5, 9)
zone_2.maximum = datetime(2022, 8, 5, 16)

zone_2.origin_reference = origin.file_set_number
zone_2.object_name = 'TIME -ZONE OBJ'




# PARAMETER
parameter_1 = Parameter()
parameter_1.long_name = 'LAT'
parameter_1.dimension = [1]
parameter_1.zones = [zone_1, zone_2]
parameter_1.values = ["40deg 23' 42.8676'' N", "40deg 23' 42.8676'' N"]
parameter_1.representation_code = 'ASCII'

parameter_1.origin_reference = origin.file_set_number
parameter_1.object_name = 'parameter_1-OBJ-NAME'


parameter_2 = Parameter()
parameter_2.long_name = 'LON'
parameter_2.dimension = [1]
parameter_2.zones = [zone_1]
parameter_2.values = ["27deg 47' 32.8956'' E"]
parameter_2.representation_code = 'ASCII'

parameter_2.origin_reference = origin.file_set_number
parameter_2.object_name = 'parameter_2-OBJ-NAME'


parameter_3 = Parameter()
parameter_3.long_name = 'SOME-FLOAT-PARAM'
parameter_3.dimension = [1]
parameter_3.values = [2378.1312]
parameter_3.units = 'm'
parameter_3.representation_code = 'FDOUBL'

parameter_3.origin_reference = origin.file_set_number
parameter_3.object_name = 'parameter_3-OBJ-NAME'




parameter_logical_record = ParameterLogicalRecord()
parameter_logical_record.parameters = [parameter_1, parameter_2, parameter_3]




# EQUIPMENT
equipment = Equipment()

equipment.trademark_name = 'EQ-TRADEMARKNAME'
equipment.status = True
equipment._type = 'Tool'
equipment.serial_number = '9101-21391'
equipment.location = 'Well'
equipment.height = 140
equipment.height_units = 'in' 
equipment.length = 230.78
equipment.length_units = 'cm'
equipment.minimum_diameter = 2.3
equipment.minimum_diameter_units = 'm'
equipment.maximum_diameter = 3.2
equipment.maximum_diameter_units = 3.2
equipment.volume = 100
equipment.volume_units = 'cm3'
equipment.weight = 1.2
equipment.weight_units = 't'
equipment.hole_size = 323.2
equipment.hole_size_units = 'm' 
equipment.pressure = 18000
equipment.pressure_units = 'psi' 
equipment.temperature = 24
equipment.temperature_units = 'degC' 
equipment.vertical_depth = 587
equipment.vertical_depth_units = 'm'
equipment.radial_drift = 23.22
equipment.radial_drift_units = 'm' 
equipment.angular_drift = 32.5
equipment.angular_drift_units = 'm' 

equipment.origin_reference = origin.file_set_number
equipment.object_name = 'SOME_EQPMNT'











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

visible_record.logical_record_segments.append(zone_1)
visible_record.logical_record_segments.append(zone_2)
visible_record.logical_record_segments.append(parameter_logical_record)
visible_record.logical_record_segments.append(equipment)

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