"""Create an exemplary DLIS file with synthetic data and all kinds of DLIS objects supported in this library."""

from datetime import datetime, timedelta
import numpy as np
import logging

from dliswriter import AttrSetup, DLISFile, enums

from utils import install_colored_logger


# colored logs output
install_colored_logger(logging.getLogger("dliswriter"))


# create DLISFile instance; optionally, pass custom parameters for file header and storage unit label
df = DLISFile(fh_id="DEFAULT FILE HEADER", fh_identifier="3")

# add origin
origin = df.add_origin("DEFAULT ORIGIN", company="XXX", order_number="352")
origin.creation_time.value = datetime(
    year=2023, month=12, day=6, hour=12, minute=30, second=5
)

# multiple origins can be added;
# the origin_reference of the first origin will be used as origin_reference in all objects automatically
# but you can also choose to pass other origins' origin_reference as the reference
# to indicate that a given object belongs to one of the other origins
origin2 = df.add_origin("ADDITIONAL ORIGIN", well_name="XYZ", company="ABC")
origin3 = df.add_origin(
    "ANOTHER ORIGIN", well_name="XYZ", company="another company", origin_reference=35
)


# define axes - metadata objects for channels
ax1 = df.add_axis(
    "AXIS1", coordinates=["40 23' 42.8676'' N", "27 47' 32.8956'' E"], axis_id="AXIS 1"
)
ax1.spacing.value = 0.2
ax1.spacing.units = enums.Unit.METER

ax2 = df.add_axis(
    "AXIS2",
    spacing=5,
    coordinates=[1, 2, 3.5],
    origin_reference=origin2.origin_reference,  # mark ax2 as belonging to origin2
)

ax3 = df.add_axis("AXIS3", spacing=0.1, coordinates=[0])


# define long_names - descriptions for channels, parameters, and computations
long_name1 = df.add_long_name("LONG-NAME1", quantity="23", standard_symbol="ABC")
long_name2 = df.add_long_name(
    "LONG-NAME-2", entity_part="X", source_part_number=["121.111"]
)
long_name3 = df.add_long_name(
    "ANOTHER LONG NAME", conditions=["At Standard Temperature"]
)


# define frame 1: depth-based with 4 channels, 100 rows each
n_rows_depth = 100
ch1 = df.add_channel(
    "DEPTH",
    data=np.arange(n_rows_depth) / 10
    - 3,  # index channel - always scalar, i.e. 1D data
    units=enums.Unit.METER,
)
ch2 = df.add_channel(
    "RPM", data=(np.arange(n_rows_depth) % 10).astype(np.int32) - 2, axis=ax3  # 1D data
)
ch3 = df.add_channel(
    "AMPLITUDE",
    data=np.random.rand(n_rows_depth, 5),  # 2D data - 5 columns
    cast_dtype=np.float32,
    long_name=long_name3,
)
ch4 = df.add_channel(
    "COMPUTED_CHANNEL",
    data=np.random.randint(0, 100, dtype=np.uint8, size=n_rows_depth),
    long_name=long_name1,
)
main_frame = df.add_frame(
    "MAIN FRAME",
    channels=(ch1, ch2, ch3, ch4),
    index_type=enums.FrameIndexType.BOREHOLE_DEPTH,
)


# define frame 2: time-based with 2 channels, 200 rows each
n_rows_time = 200
ch5 = df.add_channel(
    # index channel for frame 2
    "TIME",
    data=np.arange(n_rows_time),
    cast_dtype=np.uint32,
    units=enums.Unit.SECOND,
    axis=ax3,
)
ch6 = df.add_channel(
    "TEMPERATURE",
    data=np.random.randint(-10, 30, size=n_rows_time, dtype=np.int8),
    cast_dtype=np.int16,
    units=enums.Unit.DEGREE_CELSIUS,
)
second_frame = df.add_frame(
    "TIME FRAME", channels=(ch5, ch6), index_type=enums.FrameIndexType.NON_STANDARD
)


# zones
zone1 = df.add_zone(
    "DEPTH-ZONE", domain=enums.ZoneDomain.BOREHOLE_DEPTH, minimum=2, maximum=4.5
)
dt = datetime.now()
zone2 = df.add_zone(
    "TIME-ZONE",
    domain=enums.ZoneDomain.TIME,
    minimum=dt - timedelta(hours=3),
    maximum=dt - timedelta(minutes=30),
    origin_reference=origin3.origin_reference,  # associated with origin 3
)
zone3 = df.add_zone(
    "VDEPTH-ZONE",
    domain=enums.ZoneDomain.VERTICAL_DEPTH,
    minimum=10,
    maximum=20,
    origin_reference=origin2.origin_reference,  # associated with origin 2
)


# splices - using zones & channels
splice1 = df.add_splice(
    "SPLICE1", input_channels=(ch1,), output_channel=ch4, zones=(zone1,)
)
splice2 = df.add_splice(
    "SPLICE2", input_channels=(ch5, ch2), output_channel=ch6, zones=(zone2, zone3)
)


# parameters - using zones, axes, and long name
parameter1 = df.add_parameter(
    "PARAM1",
    long_name="Parameter nr 1",  # long_name can be str or a LongName object
    axis=ax1,
    values={
        "value": [1],
        "units": enums.Unit.INCH,
    },  # specifying value and units of the value in one line
)
parameter2 = df.add_parameter(
    "PARAM2",
    zones=(zone2,),
    long_name=long_name2,
    values=[
        ["val1", "val2", "val3"]
    ],  # specifying only values; units can be added by: parameter2.values.units = ...
    dimension=[3],
)


# equipment
# note how complex attribute values can be passed as a dict or an AttrSetup object; the effect exactly is the same
equipment1 = df.add_equipment(
    "EQ1",
    status=1,
    eq_type=enums.EquipmentType.TOOL,
    serial_number="1239-12312",
    weight={
        "value": 123.2,
        "units": enums.Unit.KILOGRAM,
    },  # specifying value and units in one line - dict version
    length=AttrSetup(
        2, enums.Unit.METER
    ),  # specifying value and units in one line - AttrSetup version
)

# 'value' and 'units' can also be added later to the created object.
equipment2 = df.add_equipment(
    "EQ2", location=enums.EquipmentLocation.WELL, trademark_name="Some trademark TM"
)
equipment2.hole_size.value = 23.5
equipment2.hole_size.units = enums.Unit.INCH

equipment3 = df.add_equipment("EQ3")
equipment3.status.value = 0


# tool - using equipment, channels, and parameters
tool1 = df.add_tool(
    "TOOL1",
    status=1,
    parts=(equipment1, equipment2),
    channels=(ch5, ch6),
    description="...",
)
tool2 = df.add_tool(
    "TOOL2",
    parameters=(parameter1, parameter2),
    channels=(ch1, ch2, ch3),
    parts=(equipment1,),
)


# computation - using axis, zones, tool, and long name
computation1 = df.add_computation(
    "CMPT1", axis=[ax1], source=tool2, zones=(zone1, zone2, zone3), dimension=[2]
)
computation1.values.value = [[1, 2], [1, 3], [1, 4]]

computation2 = df.add_computation("CMPT2", values=[2.3, 11.12312, 2231213.22])
computation3 = df.add_computation("CMPT3", values=[3.14], long_name=long_name3)


# process - using channels, computations, and parameters
process1 = df.add_process(
    "PROC",
    input_channels=(ch1, ch2),
    output_channels=(ch4,),
    input_computations=(computation1,),
    output_computations=(computation2, computation3),
    properties=[enums.Property.AVERAGED, enums.Property.LOCALLY_DEFINED],
)


# calibration coefficient
coef1 = df.add_calibration_coefficient(
    "CC1",
    label="Gain",
    coefficients=[100.1, 100.2],
    references=[122, 123],
    plus_tolerances=[2, 2.5],
    minus_tolerances=[3, 2.4],
)
coef2 = df.add_calibration_coefficient("CC2", coefficients=[1.2, 2.2, 3.4])
coef3 = df.add_calibration_coefficient("CC3", coefficients=[2])


# calibration measurement - use Axis and Channel
cmeas1 = df.add_calibration_measurement(
    "CM1",
    phase=enums.CalibrationMeasurementPhase.BEFORE,
    measurement_type="Plus",
    axis=ax1,
    measurement_source=ch1,
    measurement=[2.1, 2.5, 2.4],
    sample_count=3,
    begin_time=15,
    standard=[20, 25],
)
cmeas2 = df.add_calibration_measurement(
    "CM2",
    measurement_source=ch5,
    measurement=[30, 40, 55, 61],
    begin_time=datetime.now() - timedelta(hours=20),
)


# calibration - using calibration coefficient & measurement, channels, and parameters
calibration1 = df.add_calibration(
    "CALIB-1",
    calibrated_channels=(ch4,),
    uncalibrated_channels=(ch1, ch5),
    coefficients=(coef1, coef2, coef3),
    measurements=(cmeas1, cmeas2),
    parameters=(parameter2,),
    method="Two-point linear",
)

# well reference point
wrp = df.add_well_reference_point(
    "WELL-REF",
    coordinate_1_name="Latitude",
    coordinate_1_value=40.34,
    coordinate_2_name="Longitude",
    coordinate_2_value=23.4232,
)


# path - using frame, well reference point, and channels
# Note: DeepView doesn't open files with Path defined, but dlisio opens them fine
# path1 = df.add_path('PATH-1', frame_type=main_frame, well_reference_point=wrp, value=(ch1, ch3, ch4),
#                     borehole_depth=122.12, vertical_depth=211.1, radial_drift=12, angular_drift=1.11, time=13)
# path2 = df.add_path('PATH-2', frame_type=second_frame, value=(ch5, ch6), tool_zero_offset=1231.1, time=11.1)


# message
message1 = df.add_message(
    "MSG1", text=["Some message", "part 2 of the message"], time=datetime.now()
)
message2 = df.add_message("MSG2", text=["You have a message"], message_type="Command")
message3 = df.add_message(
    "MSG3", vertical_depth=213.1, text=["More", "text"], time=121.22
)


# comment
comment1 = df.add_comment(
    "CMT1", text=["Part 1 of the comment", "Part 2 of the comment"]
)
comment2 = df.add_comment("COMMENT-2", text=["Short comment"])


# no-format & no-format frame data
no_format1 = df.add_no_format(
    "NF1", consumer_name="Some consumer", description="Some description"
)
no_format2 = df.add_no_format("NF2", description="XYZ")
ndf1_1 = df.add_no_format_frame_data(no_format1, data="XYZ")
nfd1_2 = df.add_no_format_frame_data(no_format1, data="ABC")
nfd2_1 = df.add_no_format_frame_data(no_format2, data="Lorem ipsum")


# groups
group1 = df.add_group(
    "DEPTH ZONES", description="Zones describing depth", object_list=(zone1, zone3)
)
group2 = df.add_group("MESSAGES", object_list=(message1, message2, message3))
group3 = df.add_group("INDEX CHANNELS", object_list=(ch1, ch5))
df.add_group("ALL CHANNELS", object_list=(ch2, ch3, ch4, ch6), group_list=(group3,))
group5 = df.add_group("GROUPS", group_list=(group1, group2, group3))


# write the file
df.write("./tmp.DLIS", input_chunk_size=20, output_chunk_size=2**13)
