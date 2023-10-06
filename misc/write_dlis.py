from datetime import datetime

from dlis_writer.file.file import DLISFile
from dlis_writer.logical_record.misc.storage_unit_label import StorageUnitLabel
from dlis_writer.logical_record.misc.file_header import FileHeader
from dlis_writer.logical_record.eflr_types.origin import Origin
from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePoint
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.eflr_types.long_name import LongName
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.frame import Frame
from dlis_writer.logical_record.iflr_types.frame_data import FrameData
from dlis_writer.logical_record.eflr_types.path import Path
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.logical_record.eflr_types.equipment import Equipment
from dlis_writer.logical_record.eflr_types.tool import Tool
from dlis_writer.logical_record.eflr_types.computation import Computation
from dlis_writer.logical_record.eflr_types.process import Process
from dlis_writer.logical_record.eflr_types.calibration import CalibrationMeasurement
from dlis_writer.logical_record.eflr_types.calibration import CalibrationCoefficient
from dlis_writer.logical_record.eflr_types.calibration import Calibration
from dlis_writer.logical_record.eflr_types.group import Group
from dlis_writer.logical_record.eflr_types.splice import Splice
from dlis_writer.logical_record.eflr_types.no_format import NoFormat
from dlis_writer.logical_record.iflr_types.no_format_frame_data import NoFormatFrameData
from dlis_writer.logical_record.eflr_types.message import Message
from dlis_writer.logical_record.eflr_types.message import Comment

from dlis_writer.utils.enums import Units
from dlis_writer.utils.enums import RepresentationCode

import numpy as np
import pandas as pd


# STORAGE UNIT LABEL
sul = StorageUnitLabel('DEFAULT STORAGE SET')


# FILE HEADER
file_header = FileHeader('DEFAULT FHLR')


# ORIGIN
origin = Origin('DEFINING ORIGIN')
origin.file_id.value = 'AQLN file_id'
origin.file_set_name.value = 'AQLN file_set_name'
origin.file_set_number.value = 11
origin.file_number.value = 22
origin.file_type.value = 'AQLN file_type'
origin.product.value = 'AQLN product'
origin.version.value = 'AQLN version'
origin.programs.value = 'AQLN programs'
origin.creation_time.value = datetime.now()
origin.order_number.value = 'AQLN order_number'
origin.descent_number.value = 33
origin.run_number.value = 44
origin.well_id.value = 55
origin.well_name.value = 'AQLN well_name'
origin.field_name.value = 'AQLN field_name'
origin.producer_code.value = 1
origin.producer_name.value = 'AQLN producer_name'
origin.company.value = 'AQLN company'
origin.name_space_name.value = 'AQLN name_space_name'
origin.name_space_version.value = 66


# WELL REFERENCE POINT
well_reference_point = WellReferencePoint('AQLN WELL-REF')
well_reference_point.permanent_datum.value = 'AQLN permanent_datu'
well_reference_point.vertical_zero.value = 'AQLN vertical_zero'
well_reference_point.permanent_datum_elevation.value = 1234.51
well_reference_point.above_permanent_datum.value = 888.51
well_reference_point.magnetic_declination.value = 999.51

well_reference_point.coordinate_1_name.value = 'Lattitude'
well_reference_point.coordinate_1_value.value = 40.395240

well_reference_point.coordinate_2_name.value = 'Longitude'
well_reference_point.coordinate_2_value.value = 27.792470



# AXIS
axis = Axis('AXS-1')
axis.axis_id.value = 'FIRST AXIS'

axis.coordinates.representation_code = RepresentationCode.FDOUBL
axis.coordinates.count = 2
axis.coordinates.value = [40.395241, 27.792471]

axis.spacing.representation_code = RepresentationCode.FDOUBL
axis.spacing.value = 0.33
axis.spacing.units = Units.m


# LONG NAME
long_name = LongName('LNAME-1')
long_name.general_modifier.value = 'SOME ASCII TEXT'
long_name.quantity.value = 'SOME ASCII TEXT'
long_name.quantity_modifier.value = 'SOME ASCII TEXT'
long_name.altered_form.value = 'SOME ASCII TEXT'
long_name.entity.value = 'SOME ASCII TEXT'
long_name.entity_modifier.value = 'SOME ASCII TEXT'
long_name.entity_number.value = 'SOME ASCII TEXT'
long_name.entity_part.value = 'SOME ASCII TEXT'
long_name.entity_part_number.value = 'SOME ASCII TEXT'
long_name.generic_source.value = 'SOME ASCII TEXT'
long_name.source_part.value = 'SOME ASCII TEXT'
long_name.source_part_number.value = 'SOME ASCII TEXT'
long_name.conditions.value = 'SOME ASCII TEXT'
long_name.standard_symbol.value = 'SOME ASCII TEXT'
long_name.private_symbol.value = 'SOME ASCII TEXT'


# CHANNEL

# For each column create a Channel object defining properties of that column
depth_channel = Channel('DEPTH CHANNEL')
depth_channel.long_name.value = 'DEPTH'
depth_channel.properties.value = ['0309 AQLN PROP 1', 'PROP AQLN 2']
depth_channel.representation_code.value = RepresentationCode.FDOUBL
depth_channel.units.value = Units.m
depth_channel.dimension.value = [1]
depth_channel.element_limit.value = [1]

curve_1_channel = Channel('CURVE 1 CHANNEL')
curve_1_channel.long_name.value = 'CURVE 1'
curve_1_channel.representation_code.value = RepresentationCode.FDOUBL
curve_1_channel.units.value = Units.t
curve_1_channel.dimension.value = [1]
curve_1_channel.element_limit.value = [1]

curve_2_channel = Channel('CURVE 2 CHANNEL')
curve_2_channel.long_name.value = 'CURVE 2'
curve_2_channel.representation_code.value = RepresentationCode.FDOUBL
curve_2_channel.units.value = Units.t
curve_2_channel.dimension.value = [1]
curve_2_channel.element_limit.value = [1]

multi_dim_channel = Channel('MULTI DIM CHANNEL')
multi_dim_channel.long_name.value = 'MULTI DIMENSIONAL'
multi_dim_channel.representation_code.value = RepresentationCode.FDOUBL
multi_dim_channel.units.value = Units.t
multi_dim_channel.dimension.value = [2]
multi_dim_channel.element_limit.value = [2]

image_channel = Channel('IMG')
image_channel.long_name.value = 'IMAGE CHANNEL'
image_channel.representation_code.value = RepresentationCode.FDOUBL
image_channel.dimension.value = [384]
image_channel.element_limit.value = [384]



# FRAME
frame = Frame('MAIN')
frame.channels.value = [depth_channel, curve_1_channel, curve_2_channel, multi_dim_channel, image_channel]
frame.index_type.value = 'BOREHOLE-DEPTH'
frame.spacing.value = 0.33
frame.spacing.representation_code = RepresentationCode.FDOUBL
frame.spacing.units = 'm'

# Read Data
data = pd.read_csv('./data/data.csv')
image = pd.read_csv('./data/image.csv', header=None, sep=' ')

# Remove index col if exists 
data = data[[col for col in data.columns[1:]]]

# Convert to numpy.ndarray
data = data.values[-200:]
image = image.values[-200:]

# Create FrameData objects
frame_data_objects = []
for i in range(len(data)):

    # MERGING two columns of data.csv to test multi dimensional
    slots = np.append(data[i], [data[i][1], data[i][2]])

    # APPENDING image.csv
    slots = np.append(slots, image[i])

    frame_data = FrameData(frame=frame, frame_number=i+1, slots=slots)
    frame_data_objects.append(frame_data)

# PATH
path_1 = Path('PATH1')

path_1.frame_type.value = frame
path_1.well_reference_point.value = well_reference_point
path_1.value.value = [curve_1_channel, curve_2_channel]

path_1.vertical_depth.value = -187
path_1.vertical_depth.representation_code = RepresentationCode.SNORM

path_1.radial_drift.value = 105
path_1.radial_drift.representation_code = RepresentationCode.SSHORT

path_1.angular_drift.value = 64.23
path_1.angular_drift.representation_code = RepresentationCode.FDOUBL

path_1.time.value = 180
path_1.time.representation_code = RepresentationCode.SNORM

path_1.depth_offset.value = -123
path_1.depth_offset.representation_code = RepresentationCode.SSHORT

path_1.measure_point_offset.value = 82
path_1.measure_point_offset.representation_code = RepresentationCode.SSHORT

path_1.tool_zero_offset.value = -7
path_1.tool_zero_offset.representation_code = RepresentationCode.SSHORT



# ZONE
zone_1 = Zone('ZONE-1')
zone_1.description.value = 'BOREHOLE-DEPTH-ZONE'
zone_1.domain.value = 'BOREHOLE-DEPTH'

zone_1.maximum.value = 1300.45
zone_1.maximum.units = Units.m
zone_1.maximum.representation_code = RepresentationCode.FDOUBL

zone_1.minimum.value = 100
zone_1.minimum.units = Units.m
zone_1.minimum.representation_code = RepresentationCode.USHORT


zone_2 = Zone('ZONE-2')
zone_2.description.value = 'VERTICAL-DEPTH-ZONE'
zone_2.domain.value = 'VERTICAL-DEPTH'
zone_2.maximum.value = 2300.45
zone_2.maximum.units = Units.m
zone_2.maximum.representation_code = RepresentationCode.FDOUBL
zone_2.minimum.value = 200
zone_2.minimum.units = Units.m
zone_2.minimum.representation_code = RepresentationCode.USHORT

zone_3 = Zone('ZONE-3')
zone_3.description.value = 'ZONE-TIME'
zone_3.domain.value = 'TIME'
zone_3.maximum.value = datetime(2022, 7, 13, 11, 30)
zone_3.maximum.representation_code = RepresentationCode.DTIME
zone_3.minimum.value = datetime(2022, 7, 12, 9, 0)
zone_3.minimum.representation_code = RepresentationCode.DTIME

zone_4 = Zone('ZONE-4')
zone_4.description.value = 'ZONE-TIME-2'
zone_4.domain.value = 'TIME'
zone_4.maximum.value = 90
zone_4.maximum.units = 'minute'
zone_4.maximum.representation_code = RepresentationCode.USHORT
zone_4.minimum.value = 10
zone_4.minimum.units = 'minute'
zone_4.minimum.representation_code = RepresentationCode.USHORT


# PARAMETER
parameter_1 = Parameter('PARAM-1')
parameter_1.long_name.value = 'LATLONG-GPS'
parameter_1.dimension.value = [1]
parameter_1.zones.value = [zone_1, zone_3]
parameter_1.values.value = ["40deg 23' 42.8676'' N", "40deg 23' 42.8676'' N"]
parameter_1.values.representation_code = RepresentationCode.ASCII

parameter_2 = Parameter('PARAM-2')
parameter_2.long_name.value = 'LATLONG'
parameter_2.dimension.value = [1]
parameter_2.zones.value = [zone_2, zone_4]
parameter_2.values.value = [40.395241, 27.792471]
parameter_2.values.representation_code = RepresentationCode.FDOUBL


parameter_3 = Parameter('PARAM-3')
parameter_3.long_name.value = 'SOME-FLOAT-PARAM'
parameter_3.dimension.value = [1]
parameter_3.values.value = [2378.1312]
parameter_3.values.representation_code = RepresentationCode.FDOUBL
parameter_3.values.units = Units.m



# EQUIPMENT
equipment_1 = Equipment('EQ1')
equipment_1.trademark_name.value = 'EQ-TRADEMARKNAME'
equipment_1.status.value = 1
equipment_1._type.value = 'Tool'
equipment_1.serial_number.value = '9101-21391'
equipment_1.location.value = 'Well'
equipment_1.height.value = 140
equipment_1.height.units = Units.in_
equipment_1.length.value = 230.78
equipment_1.length.units = Units.cm
equipment_1.minimum_diameter.value = 2.3
equipment_1.minimum_diameter.units = Units.m
equipment_1.maximum_diameter.value = 3.2
equipment_1.maximum_diameter.units = Units.m
equipment_1.volume.value = 100
equipment_1.volume.units = 'cm3'
equipment_1.weight.value = 1.2
equipment_1.weight.units = Units.t
equipment_1.hole_size.value = 323.2
equipment_1.hole_size.units = Units.m 
equipment_1.pressure.value = 18000
equipment_1.pressure.units = Units.psi
equipment_1.temperature.value = 24
equipment_1.temperature.units = 'degC' 
equipment_1.vertical_depth.value = 587
equipment_1.vertical_depth.units = Units.m
equipment_1.radial_drift.value = 23.22
equipment_1.radial_drift.units = Units.m
equipment_1.angular_drift.value = 32.5
equipment_1.angular_drift.units = Units.m


equipment_2 = Equipment('EQ2')
equipment_2.trademark_name.value = 'EQ-TRADEMARKNAME'
equipment_2.status.value = 1
equipment_2._type.value = 'Tool'
equipment_2.serial_number.value = '5559101-21391'
equipment_2.location.value = 'Well'
equipment_2.height.value = 140
equipment_2.height.units = Units.in_
equipment_2.length.value = 230.78
equipment_2.length.units = Units.cm
equipment_2.minimum_diameter.value = 2.3
equipment_2.minimum_diameter.units = Units.m
equipment_2.maximum_diameter.value = 3.2
equipment_2.maximum_diameter.units = Units.m
equipment_2.volume.value = 100
equipment_2.volume.units = 'cm3'
equipment_2.weight.value = 1.2
equipment_2.weight.units = Units.t
equipment_2.hole_size.value = 323.2
equipment_2.hole_size.units = Units.m 
equipment_2.pressure.value = 18000
equipment_2.pressure.units = Units.psi 
equipment_2.temperature.value = 24
equipment_2.temperature.units = 'degC' 
equipment_2.vertical_depth.value = 587
equipment_2.vertical_depth.units = Units.m
equipment_2.radial_drift.value = 23.22
equipment_2.radial_drift.units = Units.m 
equipment_2.angular_drift.value = 32.5
equipment_2.angular_drift.units = Units.m 



# TOOL
tool = Tool('TOOL-1')
tool.description.value = 'SOME TOOL'
tool.trademark_name.value = 'SMTL'
tool.generic_name.value = 'TOOL GEN NAME'
tool.parts.value = [equipment_1, equipment_2]
tool.status.value = 1
tool.channels.value = [depth_channel, curve_1_channel]
tool.parameters.value = [parameter_1, parameter_3]


# COMPUTATION
computation_1 = Computation('COMPT-1')
computation_1.long_name.value = 'COMPT 1'
computation_1.properties.value = ['PROP 1', 'AVERAGED']
computation_1.dimension.value = [1]
computation_1.axis.value = axis
computation_1.zones.value = [zone_1, zone_2, zone_3]
computation_1.values.value = [100, 200, 300]
computation_1.values.representation_code = RepresentationCode.UNORM
computation_1.source.value = tool
computation_1.source.representation_code = RepresentationCode.OBNAME

computation_2 = Computation('COMPT-2')
computation_2.long_name.value = 'COMPT 2'
computation_2.properties.value = ['PROP 2', 'AVERAGED']
computation_2.dimension.value = [1]
computation_2.axis.value = axis
computation_2.zones.value = [zone_1, zone_2, zone_3]
computation_2.values.value = [100, 200, 300]
computation_2.values.representation_code = RepresentationCode.UNORM



# PROCESS
process_1 = Process('MERGED')
process_1.description.value = 'MERGED'
process_1.trademark_name.value = 'PROCESS 1'
process_1.version.value = '0.0.1'
process_1.properties.value = ['AVERAGED']
process_1.status.value = 'COMPLETE'
process_1.input_channels.value = [curve_1_channel]
process_1.output_channels.value = [multi_dim_channel]
process_1.input_computations.value = [computation_1]
process_1.output_computations.value = [computation_2]
process_1.parameters.value = [parameter_1, parameter_2, parameter_3]
process_1.comments.value = 'SOME COMMENT HERE'

process_2 = Process('MERGED2')
process_2.description.value = 'MERGED2'
process_2.trademark_name.value = 'PROCESS 2'
process_2.version.value = '0.0.2'
process_2.properties.value = ['AVERAGED']
process_2.status.value = 'COMPLETE'
process_2.input_channels.value = [depth_channel]
process_2.output_channels.value = [curve_2_channel]
process_2.input_computations.value = [computation_2]
process_2.output_computations.value = [computation_1]
process_2.parameters.value = [parameter_1, parameter_2, parameter_3]
process_2.comments.value = 'SOME COMMENT HERE'



# CALIBRATION MEASUREMENT
calibration_measurement_1 = CalibrationMeasurement('CMEASURE-1')
calibration_measurement_1.phase.value = 'BEFORE'
calibration_measurement_1.measurement_source.value = depth_channel
calibration_measurement_1._type.value = 'Plus'
calibration_measurement_1.dimension.value = [1]
calibration_measurement_1.measurement.value = [12.2323]
calibration_measurement_1.measurement.representation_code = RepresentationCode.FDOUBL
calibration_measurement_1.sample_count.value = [12]
calibration_measurement_1.sample_count.representation_code = RepresentationCode.USHORT
calibration_measurement_1.maximum_deviation.value = [2.2324]
calibration_measurement_1.maximum_deviation.representation_code = RepresentationCode.FDOUBL
calibration_measurement_1.standard_deviation.value = [1.123]
calibration_measurement_1.standard_deviation.representation_code = RepresentationCode.FDOUBL
calibration_measurement_1.begin_time.value = datetime.now()
calibration_measurement_1.begin_time.representation_code = RepresentationCode.DTIME
calibration_measurement_1.duration.value = 15
calibration_measurement_1.duration.representation_code = RepresentationCode.USHORT
calibration_measurement_1.duration.units = 's'
calibration_measurement_1.reference.value = [11]
calibration_measurement_1.reference.representation_code = RepresentationCode.USHORT
calibration_measurement_1.standard.value = [11.2]
calibration_measurement_1.standard.representation_code = RepresentationCode.FDOUBL
calibration_measurement_1.plus_tolerance.value = [2]
calibration_measurement_1.plus_tolerance.representation_code = RepresentationCode.USHORT
calibration_measurement_1.minus_tolerance.value = [1]
calibration_measurement_1.minus_tolerance.representation_code = RepresentationCode.USHORT



# CALIBRATION COEFFICIENT
calibration_coefficient = CalibrationCoefficient('COEF-1')
calibration_coefficient.label.value = 'Gain'
calibration_coefficient.coefficients.value = [100.2, 201.3]
calibration_coefficient.coefficients.representation_code = RepresentationCode.FDOUBL
calibration_coefficient.references.value = [89, 298]
calibration_coefficient.references.representation_code = RepresentationCode.FDOUBL
calibration_coefficient.plus_tolerances.value = [100.2, 222.124]
calibration_coefficient.plus_tolerances.representation_code = RepresentationCode.FDOUBL
calibration_coefficient.minus_tolerances.value = [87.23, 214]
calibration_coefficient.minus_tolerances.representation_code = RepresentationCode.FDOUBL




# CALIBRATION
calibration = Calibration('CALB-MAIN')
calibration.calibrated_channels.value = [depth_channel, curve_1_channel]
calibration.uncalibrated_channels.value = [curve_2_channel, multi_dim_channel, image_channel]
calibration.coefficients.value = [calibration_coefficient]
calibration.measurements.value = [calibration_measurement_1]
calibration.parameters.value = [parameter_1, parameter_2, parameter_3]
calibration.method.value = 'Two-Point-Linear'



# GROUP
group_1 = Group('GRP-1')
group_1.description.value = 'MULTI-DIMENSIONAL CHANNELS'
group_1.object_type.value = 'CHANNEL'
group_1.object_list.value = [multi_dim_channel, image_channel]


# SPLICE
splice_1 = Splice('SPLICE-1')
splice_1.output_channels.value = multi_dim_channel
splice_1.input_channels.value = [curve_1_channel, curve_2_channel]
splice_1.zones.value = [zone_1, zone_2, zone_3, zone_4]


# NO FORMAT
no_format_1 = NoFormat('no_format_1')
no_format_1.consumer_name.value = 'SOME TEXT NOT FORMATTED'
no_format_1.description.value = 'TESTING-NO-FORMAT'

no_format_2 = NoFormat('no_format_2')
no_format_2.consumer_name.value = 'SOME IMAGE NOT FORMATTED'
no_format_2.description.value = 'TESTING-NO-FORMAT-2'

no_format_fdata_1 = NoFormatFrameData()
no_format_fdata_1.no_format_object = no_format_1
no_format_fdata_1.data = 'Some text that is recorded but never read by anyone.'

no_format_fdata_2 = NoFormatFrameData()
no_format_fdata_2.no_format_object = no_format_1
no_format_fdata_2.data = 'Some OTHER text that is recorded but never read by anyone.'

no_format_fdata_3 = NoFormatFrameData()
no_format_fdata_3.no_format_object = no_format_2
no_format_fdata_3.data = 'This could be the BINARY data of an image rather than ascii text'


# MESSAGE
message_1 = Message('MESSAGE-1')
message_1._type.value = 'Command'
message_1.time.value = datetime.now()
message_1.time.representation_code = RepresentationCode.DTIME
message_1.borehole_drift.value = 123.34
message_1.borehole_drift.representation_code = RepresentationCode.FDOUBL
message_1.vertical_depth.value = 234.45
message_1.vertical_depth.representation_code = RepresentationCode.FDOUBL
message_1.radial_drift.value = 345.56
message_1.radial_drift.representation_code = RepresentationCode.FDOUBL
message_1.angular_drift.value = 456.67
message_1.angular_drift.representation_code = RepresentationCode.FDOUBL
message_1.text.value = 'Test message 11111'



# COMMENT
comment_1 = Comment('COMMENT-1')
comment_1.text.value = 'SOME COMMENT HERE'


comment_2 = Comment('COMMENT-2')
comment_2.text.value = 'SOME OTHER COMMENT HERE'


# CREATE THE FILE
dlis_file = DLISFile(file_path='./output/test.DLIS',
                     storage_unit_label=sul,
                     file_header=file_header,
                     origin=origin)

dlis_file.logical_records.append(well_reference_point)
dlis_file.logical_records.append(axis)
dlis_file.logical_records.append(long_name)
dlis_file.logical_records.append(depth_channel)
dlis_file.logical_records.append(curve_1_channel)
dlis_file.logical_records.append(curve_2_channel)
dlis_file.logical_records.append(multi_dim_channel)
dlis_file.logical_records.append(image_channel)
dlis_file.logical_records.append(frame)

for fdata in frame_data_objects:
    dlis_file.logical_records.append(fdata)

dlis_file.logical_records.append(path_1)
dlis_file.logical_records.append(zone_1)
dlis_file.logical_records.append(zone_2)
dlis_file.logical_records.append(zone_3)
dlis_file.logical_records.append(zone_4)
dlis_file.logical_records.append(parameter_1)
dlis_file.logical_records.append(parameter_2)
dlis_file.logical_records.append(parameter_3)
dlis_file.logical_records.append(equipment_1)
dlis_file.logical_records.append(equipment_2)
dlis_file.logical_records.append(tool)
dlis_file.logical_records.append(computation_1)
dlis_file.logical_records.append(computation_2)
dlis_file.logical_records.append(process_1)
dlis_file.logical_records.append(process_2)
dlis_file.logical_records.append(calibration_measurement_1)
dlis_file.logical_records.append(calibration_coefficient)
dlis_file.logical_records.append(calibration)
dlis_file.logical_records.append(group_1)
dlis_file.logical_records.append(splice_1)
dlis_file.logical_records.append(no_format_1)
dlis_file.logical_records.append(no_format_2)
dlis_file.logical_records.append(no_format_fdata_1)
dlis_file.logical_records.append(no_format_fdata_2)
dlis_file.logical_records.append(no_format_fdata_3)
dlis_file.logical_records.append(message_1)
dlis_file.logical_records.append(comment_1)
dlis_file.logical_records.append(comment_2)

print('Please wait...')
dlis_file.write_dlis()
print('done...')