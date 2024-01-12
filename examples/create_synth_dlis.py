from datetime import datetime, timedelta
import numpy as np
import logging

from dlis_writer.file import DLISFile
from dlis_writer.logical_record.eflr_types.origin import OriginItem
from dlis_writer.utils.logging import install_logger
from dlis_writer.utils.enums import RepresentationCode


# colored logs output
logger = logging.getLogger(__name__)
install_logger(logger)


# set up origin & file header with custom parameters - by creating an instance or dict of kwargs
origin = OriginItem("DEFAULT ORIGIN", file_set_number=1, company="XXX")
origin.creation_time.value = datetime(year=2023, month=12, day=6, hour=12, minute=30, second=5)
file_header = {'sequence_number': 2}


# create DLISFile instance, pass the origin and file header
df = DLISFile(origin=origin, file_header=file_header)


# change parameters of already added objects
df.origin.order_number.value = "352"


# define axes - metadata objects for channels
ax1 = df.add_axis('AXIS1', coordinates=["40 23' 42.8676'' N", "27 47' 32.8956'' E"], axis_id='AXIS 1')
ax1.spacing.value = 0.2
ax1.spacing.units = 'm'
ax2 = df.add_axis('AXIS2', spacing=5, coordinates=[1, 2, 3.5])


# define frame 1: depth-based with 4 channels, 100 rows each
n_rows_depth = 100
ch1 = df.add_channel('DEPTH', data=np.arange(n_rows_depth) / 10 - 3, units='m')   # index channel - always scalar
ch2 = df.add_channel("RPM", data=(np.arange(n_rows_depth) % 10).astype(np.int32) - 2, axis=ax1)  # 1D data
ch3 = df.add_channel("AMPLITUDE", data=np.random.rand(n_rows_depth, 5), cast_dtype=np.float32)  # 2D data
ch4 = df.add_channel('COMPUTED_CHANNEL', data=np.random.randint(0, 100, dtype=np.uint8, size=n_rows_depth))
main_frame = df.add_frame("MAIN FRAME", channels=(ch1, ch2, ch3, ch4), index_type='BOREHOLE-DEPTH')


# define frame 2: time-based with 2 channels, 200 rows each
n_rows_time = 200
ch5 = df.add_channel(
    'TIME', data=np.arange(n_rows_time), cast_dtype=np.uint32, units='s', axis=ax2)  # index channel for frame 2
ch6 = df.add_channel(
    'TEMPERATURE', data=np.random.randint(-10, 30, size=n_rows_time, dtype=np.int8),
    cast_dtype=np.int16, units='degC')
second_frame = df.add_frame('TIME FRAME', channels=(ch5, ch6), index_type='NON-STANDARD')


# zones
zone1 = df.add_zone('DEPTH-ZONE', domain='BOREHOLE-DEPTH', minimum=2, maximum=4.5)
dt = datetime.now()
zone2 = df.add_zone('TIME-ZONE', domain='TIME', minimum=dt - timedelta(hours=3), maximum=dt - timedelta(minutes=30))
zone3 = df.add_zone('VDEPTH-ZONE', domain='VERTICAL-DEPTH', minimum=10, maximum=20)


# splices - using zones & channels
splice1 = df.add_splice('SPLICE1', input_channels=(ch1, ch2), output_channel=ch4, zones=(zone1,))
splice2 = df.add_splice('SPLICE2', input_channels=(ch5,), output_channel=ch6, zones=(zone2, zone3))


# parameters - using zones and axes
parameter1 = df.add_parameter('PARAM1', long_name="Parameter nr 1", axis=ax1, zones=(zone1,), values=[1, 2, 3.3])
parameter1.values.units = 'in'
parameter2 = df.add_parameter('PARAM2', zones=(zone2, zone3), values=["val1", "val2", "val3"], dimension=[3])


# equipment
equipment1 = df.add_equipment("EQ1", status=1, eq_type='Tool', serial_number='1239-12312', weight=123.2, length=2)
equipment1.weight.units = 'kg'
equipment1.length.units = 'm'
equipment1.length.representation_code = RepresentationCode.UNORM

equipment2 = df.add_equipment("EQ2", location='Well', trademark_name='Some trademark TM')
equipment2.hole_size.value = 23.5
equipment2.hole_size.units = 'in'
equipment2.hole_size.representation_code = 'FSINGL'  # type: ignore  # using converter associated with the property
# ^ can use the enum member, name (str), or value (int)

equipment3 = df.add_equipment('EQ3')
equipment3.status.value = 0


# tool - using equipment, channels, and parameters
tool1 = df.add_tool('TOOL1', status=1, parts=(equipment1, equipment2), channels=(ch5, ch6), description='...')
tool2 = df.add_tool('TOOL2', parameters=(parameter1, parameter2), channels=(ch1, ch2, ch3), parts=(equipment1,))


# computation - using axis, zones, and tool
computation1 = df.add_computation('CMPT1', axis=ax1, source=tool2, zones=(zone1, zone2, zone3), dimension=[3])
computation1.values.value = [1, 2, 3]
computation2 = df.add_computation('CMPT2', values=[2.3, 11.12312, 2231213.22])
computation3 = df.add_computation('CMPT3', values=[3.14])


# process - using channels, computations, and parameters
process1 = df.add_process("PROC", input_channels=(ch1, ch2), output_channels=(ch4,), input_computations=(computation1,),
                          output_computations=(computation2, computation3), properties=['a', 'b', 'c'])


# calibration coefficient
coef1 = df.add_calibration_coefficient('CC1', label='Gain', coefficients=[100.1, 100.2], references=[122, 123],
                                       plus_tolerances=[2, 2.5], minus_tolerances=[3, 2.4])
coef2 = df.add_calibration_coefficient('CC2', coefficients=[1.2, 2.2, 3.4])
coef3 = df.add_calibration_coefficient('CC3', coefficients=[2])


# calibration measurement - use Axis and Channel
cmeas1 = df.add_calibration_measurement('CM1', phase='BEFORE', measurement_type='Plus', axis=ax1,
                                        measurement_source=ch1, measurement=[2.1, 2.5, 2.4], sample_count=3,
                                        begin_time=15, standard=[20, 25])
cmeas2 = df.add_calibration_measurement('CM2', measurement_source=ch5, measurement=[30, 40, 55, 61],
                                        begin_time=datetime.now()-timedelta(hours=20))


# calibration - using calibration coefficient & measurement, channels, and parameters
calibration1 = df.add_calibration('CALIB-1', calibrated_channels=(ch4,), uncalibrated_channels=(ch1, ch5),
                                  coefficients=(coef1, coef2, coef3), measurements=(cmeas1, cmeas2),
                                  parameters=(parameter2,), method='Two-point linear')

# well reference point
wrp = df.add_well_reference_point("WELL-REF", coordinate_1_name="Latitude", coordinate_1_value=40.34,
                                  coordinate_2_name='Longitude', coordinate_2_value=23.4232)


# path - using frame, well reference point, and channels
# Note: DeepView doesn't open files with Path defined - to be fixed
# example for future use:
# path1 = df.add_path('PATH-1', frame_type=main_frame, well_reference_point=wrp, value=(ch1, ch3, ch4),
#                     borehole_depth=122.12, vertical_depth=211.1, radial_drift=12, angular_drift=1.11, time=13)
# path2 = df.add_path('PATH-2', frame_type=second_frame, value=(ch5, ch6), tool_zero_offset=1231.1, time=11.1)


# message
message1 = df.add_message('MSG1', text=["Some message", "part 2 of the message"], time=datetime.now())
message2 = df.add_message("MSG2", text=["You have a message"], message_type="Command")
message3 = df.add_message("MSG3", vertical_depth=213.1, text=["More", "text"], time=121.22)


# comment
comment1 = df.add_comment("CMT1", text=["Part 1 of the comment", "Part 2 of the comment"])
comment2 = df.add_comment("COMMENT-2", text=["Short comment"])


# long name
long_name1 = df.add_long_name("LONG-NAME1", quantity="23", standard_symbol="ABC")


# no-format & no-format frame data
no_format1 = df.add_no_format("NF1", consumer_name="Some consumer", description="Some description")
no_format2 = df.add_no_format("NF2", description="XYZ")
ndf1_1 = df.add_no_format_frame_data(no_format1, data="XYZ")
nfd1_2 = df.add_no_format_frame_data(no_format1, data="ABC")
nfd2_1 = df.add_no_format_frame_data(no_format2, data="Lorem ipsum")


# groups
group1 = df.add_group("DEPTH ZONES", description='Zones describing depth', object_type='ZONE',
                      object_list=(zone1, zone3))
group2 = df.add_group("MESSAGES", object_type="MESSAGE", object_list=(message1, message2, message3))
group3 = df.add_group("INDEX CHANNELS", object_type="CHANNEL", object_list=(ch1, ch5))
df.add_group("ALL CHANNELS", object_type="CHANNEL", object_list=(ch2, ch3, ch4, ch6), group_list=(group3,))
group5 = df.add_group("GROUPS", group_list=(group1, group2, group3))


# write the file
df.write('./tmp.DLIS', input_chunk_size=20, output_chunk_size=2**13)
