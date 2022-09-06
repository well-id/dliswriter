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
from logical_record import Tool
from logical_record import ToolLogicalRecord
from logical_record import Computation
from logical_record import ComputationLogicalRecord
from logical_record import Process
from logical_record import ProcessLogicalRecord
from logical_record import CalibrationMeasurement
from logical_record import CalibrationMeasurementLogicalRecord
from logical_record import CalibrationCoefficient
from logical_record import CalibrationCoefficientLogicalRecord


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



# TOOL

tool_1 = Tool()

tool_1.description = 'TOOL 1'
tool_1.trademark_name = 'AQLN TOOL 1'
tool_1.generic_name = 'SOME TOOL'
tool_1.parts = [equipment]
tool_1.status = True
tool_1.channels = [curve_1_channel, curve_2_channel]
tool_1.parameters = [parameter_1, parameter_2]

tool_1.origin_reference = origin.file_set_number
tool_1.object_name = 'FIRST TOOL'



tool_2 = Tool()

tool_2.description = 'TOOL for DEPTH'
tool_2.trademark_name = 'AQLN DEPTH TOOL'
tool_2.generic_name = 'SOME TOOL for DEPTH'
tool_2.parts = [equipment]
tool_2.status = True
tool_2.channels = [depth_channel]
tool_2.parameters = [parameter_1, parameter_2]

tool_2.origin_reference = origin.file_set_number
tool_2.object_name = 'DEPTH TOOL'


tool_logical_record = ToolLogicalRecord()
tool_logical_record.tools = [tool_1, tool_2]



# COMPUTATION
computation_1 = Computation()
computation_1.long_name = 'Average'
computation_1.properties = ['AVERAGED']
computation_1.dimension = [1]
computation_1.zones = [zone_1, zone_2]
computation_1.values = [112.124, 42.23]
computation_1.representation_code = 'FDOUBL'
computation_1.units = 'm'

computation_1.origin_reference = origin.file_set_number
computation_1.object_name = 'computation_1 OBJ NAME'


computation_2 = Computation()
computation_2.long_name = 'Normalization'
computation_2.properties = ['NORMALIZED', 'AVERAGED']
computation_2.dimension = [1]
computation_2.zones = [zone_1, zone_2]
computation_2.values = [0.876, 0.564]
computation_2.representation_code = 'FDOUBL'
computation_2.units = 'm'

computation_2.origin_reference = origin.file_set_number
computation_2.object_name = 'computation_2 OBJ NAME'


computation_logical_record = ComputationLogicalRecord()
computation_logical_record.computations = [computation_1, computation_2]



# PROCESS
process_1 = Process()
process_1.description = 'Process 1'
process_1.trademark_name = 'Proc 1 TMN'
process_1.version = '1.0.0'
process_1.properties = ['NOPROP']
process_1.status = 'COMPLETE'
process_1.input_channels = [depth_channel]
process_1.output_channels = [curve_1_channel]
process_1.input_computations = [computation_1]
process_1.output_computations = [computation_2]
process_1.parameters = [parameter_1, parameter_2, parameter_3]
process_1.comments = 'These are dummy values for testing'
process_1.origin_reference = origin.file_set_number
process_1.object_name = 'PROC-1 OBJ-NAME'

process_2 = Process()
process_2.description = 'Process 2'
process_2.trademark_name = 'Proc 2 TMN'
process_2.version = '2.0.0'
process_2.properties = ['AVERAGED']
process_2.status = 'IN-PROGRESS'
process_2.input_channels = [curve_1_channel]
process_2.output_channels = [curve_2_channel]
process_2.input_computations = [computation_1]
process_2.output_computations = [computation_2]
process_2.parameters = [parameter_1]
process_2.comments = 'These are dummy values for testing'
process_2.origin_reference = origin.file_set_number
process_2.object_name = 'PROC-2 OBJ-NAME'


process_3 = Process()
process_3.description = 'Process 3'
process_3.trademark_name = 'Proc 3 TMN'
process_3.version = '3.0.0'
process_3.properties = ['PROP-3']
process_3.status = 'ABORTED'
process_3.input_channels = [depth_channel]
process_3.output_channels = [curve_1_channel]
process_3.input_computations = [computation_1]
process_3.output_computations = [computation_2]
process_3.parameters = [parameter_1, parameter_2, parameter_3]
process_3.comments = 'These are dummy values for testing'
process_3.origin_reference = origin.file_set_number
process_3.object_name = 'PROC-3 OBJ-NAME'



process_logical_record = ProcessLogicalRecord()
process_logical_record.processes = [process_1, process_2, process_3]



# CALIBRATION MEASUREMENT
calibration_measurement_1 = CalibrationMeasurement()
calibration_measurement_1.origin_reference = origin.file_set_number
calibration_measurement_1.object_name = 'calibration_measurement_1 OBJ-NAME'
calibration_measurement_1.phase = 'BEFORE'
calibration_measurement_1.measurement_source = depth_channel
calibration_measurement_1._type = 'Plus'
calibration_measurement_1.dimension = [1]
calibration_measurement_1.measurement = [12.2323]
calibration_measurement_1.measurement_representation_code = 'FDOUBL'
calibration_measurement_1.sample_count = [12]
calibration_measurement_1.maximum_deviation = [2.2324]
calibration_measurement_1.standard_deviation = [1.123]
calibration_measurement_1.begin_time = datetime.now()
calibration_measurement_1.duration = 15
calibration_measurement_1.duration_representation_code = 'USHORT'
calibration_measurement_1.duration_units = 's'
calibration_measurement_1.reference = [11]
calibration_measurement_1.reference_representation_code = 'USHORT'
calibration_measurement_1.standard = [11.2]
calibration_measurement_1.standard_representation_code = 'FDOUBL'
calibration_measurement_1.plus_tolerance = [2]
calibration_measurement_1.minus_tolerance = [1]


calibration_measurement_2 = CalibrationMeasurement()
calibration_measurement_2.origin_reference = origin.file_set_number
calibration_measurement_2.object_name = 'calibration_measurement_2 OBJ-NAME'
calibration_measurement_2.phase = 'AFTER'
calibration_measurement_2.measurement_source = curve_1_channel
calibration_measurement_2._type = 'Zero'
calibration_measurement_2.dimension = [1]
calibration_measurement_2.measurement = [12.2323]
calibration_measurement_2.measurement_representation_code = 'FDOUBL'
calibration_measurement_2.sample_count = [12]
calibration_measurement_2.maximum_deviation = [2.2324]
calibration_measurement_2.standard_deviation = [1.123]
calibration_measurement_2.begin_time = datetime.now()
calibration_measurement_2.duration = 20
calibration_measurement_2.duration_representation_code = 'USHORT'
calibration_measurement_2.duration_units = 's'
calibration_measurement_2.reference = [11]
calibration_measurement_2.reference_representation_code = 'USHORT'
calibration_measurement_2.standard = [11.2]
calibration_measurement_2.standard_representation_code = 'FDOUBL'
calibration_measurement_2.plus_tolerance = [2]
calibration_measurement_2.minus_tolerance = [1]



calibration_measurement_logical_record = CalibrationMeasurementLogicalRecord()
calibration_measurement_logical_record.calibration_measurements = [calibration_measurement_1, calibration_measurement_2]




# CALIBRATION COEFFICIENTS
calibration_coefficient_1 = CalibrationCoefficient()
calibration_coefficient_1.origin_reference = origin.file_set_number
calibration_coefficient_1.object_name = 'calibration_coefficient_1 OBJ NAME'
calibration_coefficient_1.label = 'COEF-1'
calibration_coefficient_1.coefficients = [12.12, 34.34, 14.23]
calibration_coefficient_1.references = [11, 32.2, 15.542]
calibration_coefficient_1.plus_tolerances = [1.2, 3.6, 2.023]
calibration_coefficient_1.minus_tolerances = [0.98, 2.89, 1.978]


calibration_coefficient_2 = CalibrationCoefficient()
calibration_coefficient_2.origin_reference = origin.file_set_number
calibration_coefficient_2.object_name = 'calibration_coefficient_2 OBJ NAME'
calibration_coefficient_2.label = 'COEF-2'
calibration_coefficient_2.coefficients = [12.12, 34.34, 14.23]
calibration_coefficient_2.references = [11, 32.2, 15.542]
calibration_coefficient_2.plus_tolerances = [1.2, 3.6, 2.023]
calibration_coefficient_2.minus_tolerances = [0.98, 2.89, 1.978]


calibration_coefficient_logical_record = CalibrationCoefficientLogicalRecord()
calibration_coefficient_logical_record.calibration_coefficients = [calibration_coefficient_1, calibration_coefficient_2]



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
visible_record.logical_record_segments.append(tool_logical_record)
visible_record.logical_record_segments.append(computation_logical_record)
visible_record.logical_record_segments.append(process_logical_record)
visible_record.logical_record_segments.append(calibration_measurement_logical_record)
visible_record.logical_record_segments.append(calibration_coefficient_logical_record)













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