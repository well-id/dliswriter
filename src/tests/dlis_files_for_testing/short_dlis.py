import os
from typing import Union
import numpy as np
from datetime import datetime

from dlis_writer.file import DLISFile
from dlis_writer.logical_record import eflr_types

from tests.dlis_files_for_testing.common import make_file_header, make_sul


def _add_origin(df: DLISFile) -> eflr_types.OriginItem:
    origin = df.add_origin(
        "DEFAULT ORIGIN",
        creation_time="2050/03/02 15:30:00",
        file_set_name="Test file set name",
        file_set_number=42,
        file_number=8,
        run_number=13,
        well_id=5,
        well_name="Test well name",
        field_name="Test field name",
        company="Test company"
    )

    return origin


def _add_frame(df: DLISFile, *channels: eflr_types.ChannelItem) -> eflr_types.FrameItem:
    fr = df.add_frame(
        "MAIN FRAME",
        channels=channels,
        index_type="TIME",
        spacing=0.5,
        encrypted=1,
        description="Frame description"
    )

    fr.spacing.units = "s"
    return fr


def _add_channels(df: DLISFile, ax1: eflr_types.AxisItem) -> tuple[eflr_types.ChannelItem, ...]:
    ch = df.add_channel(
        name="Some Channel",
        dataset_name="image1",
        long_name="Some not so very long channel name",
        properties=["AVERAGED", "locally-defined", "Speed corrected"],
        cast_dtype=np.float32,
        units="acre",
        dimension=12,
        axis=ax1,
        element_limit=12,
        minimum_value=0,
        maximum_value=127.6,
    )

    ch1 = df.add_channel(name="Channel 1", dimension=[10, 10], units="in")
    ch2 = df.add_channel("Channel 2")
    ch3 = df.add_channel("Channel 13", dataset_name='amplitude', element_limit=128)
    ch_time = df.add_channel("posix time", dataset_name="contents/time", units="s")
    ch_rpm = df.add_channel("surface rpm", dataset_name="contents/rpm")
    ch_amplitude = df.add_channel("amplitude", dataset_name="contents/image0", dimension=128)
    ch_radius = df.add_channel("radius", dataset_name="contents/image1", dimension=128, units="in")
    ch_radius_pooh = df.add_channel("radius_pooh", dataset_name="contents/image2", units="m")
    ch_x = df.add_channel("channel_x", long_name="Channel not added to the frame", dataset_name="image2", units="s")

    return ch, ch1, ch2, ch3, ch_time, ch_rpm, ch_amplitude, ch_radius, ch_radius_pooh, ch_x


def _add_axes(df: DLISFile) -> tuple[eflr_types.AxisItem, ...]:
    ax1 = df.add_axis(
        name="Axis-1",
        axis_id="First axis",
        coordinates=[40.395241, 27.792471],
        spacing=0.33
    )
    ax1.spacing.units = "m"

    ax2 = df.add_axis(
        "Axis-X",
        axis_id="Axis not added to computation",
        coordinates=[8],
        spacing=2
    )
    ax2.spacing.units = "m"

    return ax1, ax2


def _add_zones(df: DLISFile) -> tuple[eflr_types.ZoneItem, ...]:
    z1 = df.add_zone(
        name="Zone-1",
        description="BOREHOLE-DEPTH-ZONE",
        domain="BOREHOLE-DEPTH",
        maximum=1300,
        minimum=100
    )
    z1.maximum.units = "m"
    z1.minimum.units = "m"

    z2 = df.add_zone(
        "Zone-2",
        description="VERTICAL-DEPTH-ZONE",
        domain="VERTICAL-DEPTH",
        maximum=2300.45,
        minimum=200.0
    )
    z2.maximum.units = "m"
    z2.minimum.units = "m"

    z3 = df.add_zone(
        "Zone-3",
        description="ZONE-TIME",
        domain="TIME",
        maximum="2050/07/13 11:30:00",
        minimum="2050/07/12 9:00:00"
    )

    z4 = df.add_zone(
        "Zone-4",
        description="ZONE-TIME-2",
        domain="TIME",
        maximum=90,
        minimum=10
    )
    z4.maximum.units = "min"
    z4.minimum.units = "min"

    zx = df.add_zone(
        name="Zone-X",
        description="Zone not added to any parameter",
        domain="TIME",
        maximum=10,
        minimum=1,
    )
    zx.maximum.units = "s"
    zx.minimum.units = "s"

    return z1, z2, z3, z4, zx


def _add_parameters(df: DLISFile, zones: tuple[eflr_types.ZoneItem, ...]) -> tuple[eflr_types.ParameterItem, ...]:
    p1 = df.add_parameter(
        name="Param-1",
        long_name="LATLONG-GPS",
        zones=[zones[0], zones[2]],
        values=["40deg 23' 42.8676'' N", "40deg 23' 42.8676'' N"]
    )

    p2 = df.add_parameter(
        name="Param-2",
        long_name="LATLONG",
        zones=[zones[1], zones[3]],
        values=[40.395241, 27.792471],
    )

    p3 = df.add_parameter(
        name="Param-3",
        long_name="SOME-FLOAT-PARAM",
        values=[12.5]
    )
    p3.values.units = "m"

    return p1, p2, p3


def _add_equipment(df: DLISFile) -> tuple[eflr_types.EquipmentItem, ...]:
    eq1 = df.add_equipment(
        name="EQ1",
        trademark_name="EQ-TRADEMARKNAME",
        status=1,
        eq_type="Tool",
        serial_number="9101-21391",
        location="Well",
        height=140,
        length=230.78,
        minimum_diameter=2.3,
        maximum_diameter=3.2,
        volume=100,
        weight=1.2,
        hole_size=323.2,
        pressure=18000,
        temperature=24,
        vertical_depth=587,
        radial_drift=23.22,
        angular_drift=32.5,
    )

    eq1.height.units = "in"
    eq1.length.units = "cm"
    eq1.minimum_diameter.units = "m"
    eq1.maximum_diameter.units = "m"
    eq1.weight.units = "t"
    eq1.hole_size.units = "m"
    eq1.pressure.units = "psi"
    eq1.temperature.units = "degC"
    eq1.vertical_depth.units = "m"
    eq1.radial_drift.units = "m"
    eq1.angular_drift.units = "m"

    eq2 = df.add_equipment(
        name="EQ2",
        trademark_name="EQ-TRADEMARKNAME",
        status=0,
        eq_type="Tool",
        serial_number="5559101-21391"
    )

    eq3 = df.add_equipment(
        name="EqX",
        trademark_name="EQ-TRADEMARKNAME",
        status=1,
        eq_type="Tool",
        serial_number="12311"
    )

    return eq1, eq2, eq3


def _add_tools(df: DLISFile, equipment: tuple[eflr_types.EquipmentItem, ...],
               parameters: tuple[eflr_types.ParameterItem, ...], channels: tuple[eflr_types.ChannelItem, ...]) \
        -> tuple[eflr_types.ToolItem, ...]:
    t1 = df.add_tool(
        name="TOOL-1",
        description="SOME TOOL",
        trademark_name="SMTL",
        generic_name="TOOL GEN NAME",
        parts=[equipment[0], equipment[1]],
        status=1,
        channels=[channels[4], channels[6]],
        parameters=[parameters[0], parameters[2]]
    )

    t2 = df.add_tool(
        name="Tool-X",
        description="desc",
        trademark_name="SMTL",
        generic_name="TOOL GEN NAME",
        parts=[equipment[1]],
        status=0,
        channels=[channels[8]],
        parameters=[parameters[1]]
    )

    return t1, t2


def _add_processes(df: DLISFile, parameters: tuple[eflr_types.ParameterItem, ...],
                   channels: tuple[eflr_types.ChannelItem, ...], computations: tuple[eflr_types.ComputationItem, ...]) \
        -> tuple[eflr_types.ProcessItem, ...]:
    p1 = df.add_process(
        name="Process 1",
        description="MERGED",
        trademark_name="PROCESS 1",
        version="0.0.1",
        properties=["AVERAGED"],
        status="COMPLETE",
        input_channels=[channels[7]],
        output_channels=[channels[6], channels[2]],
        input_computations=[computations[0]],
        output_computations=[computations[1]],
        parameters=parameters,
        comments=["SOME COMMENT HERE"]
    )

    p2 = df.add_process(
        name="Prc2",
        description="MERGED2",
        trademark_name="PROCESS 2",
        version="0.0.2",
        properties=["AVERAGED"],
        status="COMPLETE",
        input_channels=[channels[1]],
        output_channels=[channels[2]],
        input_computations=[computations[1], computations[0]],
        parameters=[parameters[0]],
        comments=["Other comment"]
    )

    return p1, p2


def _add_computation(df: DLISFile, axes: tuple[eflr_types.AxisItem, ...], zones: tuple[eflr_types.ZoneItem, ...],
                     tools: tuple[eflr_types.ToolItem, ...]) -> tuple[eflr_types.ComputationItem, ...]:
    c1 = df.add_computation(
        name="COMPT-1",
        long_name="COMPT1",
        properties=["locally defined", "AVERAGED"],
        dimension=[1],
        axis=axes[0],
        zones=zones[:3],
        values=[100, 200, 300],
        source=tools[0]
    )

    c2 = df.add_computation(
        name="COMPT2",
        long_name="COMPT 2",
        properties=["under-sampled", "AVERAGED"],
        axis=axes[0],
        zones=[zones[0], zones[2]],
        values=[1.5, 2.5]
    )

    cx = df.add_computation(
        name="COMPT-X",
        long_name="Computation not added to process",
        properties=["over_sampled"],
        axis=axes[0],
        zones=[zones[2]],
        values=[12],
    )

    return c1, c2, cx


def _add_splices(df: DLISFile, channels: tuple[eflr_types.ChannelItem, ...], zones: tuple[eflr_types.ZoneItem, ...]) \
        -> tuple[eflr_types.SpliceItem]:
    s = df.add_splice(
        name="splc1",
        output_channel=channels[6],
        input_channels=[channels[1], channels[2]],
        zones=[zones[0], zones[1]]
    )

    return s,


def _add_calibrations(df: DLISFile, axes: tuple[eflr_types.AxisItem, ...],
                      channels: tuple[eflr_types.ChannelItem, ...],
                      parameters: tuple[eflr_types.ParameterItem, ...]) \
        -> tuple[
            eflr_types.CalibrationMeasurementItem,
            eflr_types.CalibrationCoefficientItem,
            eflr_types.CalibrationItem]:
    cm = df.add_calibration_measurement(
        name="CMEASURE-1",
        phase="BEFORE",
        axis=axes[0],
        measurement_source=channels[1],
        measurement_type="Plus",
        measurement=[12.2323],
        sample_count=12,
        maximum_deviation=2.2324,
        standard_deviation=1.123,
        begin_time=datetime(year=2050, month=3, day=12, hour=12, minute=30),
        duration=15,
        reference=[11],
        standard=[11.2],
        plus_tolerance=[2],
        minus_tolerance=[1],
    )
    cm.duration.units = "s"

    cc = df.add_calibration_coefficient(
        name="COEF-1",
        label="Gain",
        coefficients=[100.2, 201.3],
        references=[89, 298],
        plus_tolerances=[100.2, 222.124],
        minus_tolerances=[87.23, 214],
    )

    c = df.add_calibration(
        name="CALIB-MAIN",
        calibrated_channels=[channels[1], channels[2]],
        uncalibrated_channels=[channels[6], channels[7], channels[8]],
        coefficients=[cc],
        measurements=[cm],
        parameters=parameters,
        method="Two Point Linear"
    )

    return cm, cc, c


def _add_well_reference_points(df: DLISFile) -> tuple[eflr_types.WellReferencePointItem, ...]:
    w1 = df.add_well_reference_point(
        name="AQLN WELL-REF",
        permanent_datum="AQLN permanent_datum",
        vertical_zero="AQLN vertical_zero",
        permanent_datum_elevation=1234.51,
        above_permanent_datum=888.51,
        magnetic_declination=999.51,
        coordinate_1_name="Latitude",
        coordinate_1_value=40.395240,
        coordinate_2_name="Longitude",
        coordinate_2_value=27.792470
    )

    w2 = df.add_well_reference_point(
        name="WRP-X",
        permanent_datum="pd1",
        vertical_zero="vz20",
        permanent_datum_elevation=32.5,
        above_permanent_datum=100,
        magnetic_declination=112.3,
        coordinate_1_name="X",
        coordinate_1_value=20,
        coordinate_2_name="Y",
        coordinate_2_value=-0.3,
        coordinate_3_name="Z",
        coordinate_3_value=1
    )

    return w1, w2


def _add_paths(df: DLISFile, frame: eflr_types.FrameItem, wrp: eflr_types.WellReferencePointItem,
               channels: tuple[eflr_types.ChannelItem, ...]) -> tuple[eflr_types.PathItem, ...]:
    path1 = df.add_path(
        'PATH-1',
        frame_type=frame,
        well_reference_point=wrp,
        value=(channels[0], channels[1], channels[2]),
        borehole_depth=122.12,
        vertical_depth=211.1,
        radial_drift=12,
        angular_drift=1.11,
        time=13
    )

    path2 = df.add_path('PATH-2', value=(channels[4],), tool_zero_offset=1231.1, time=11.1)

    return path1, path2


def _add_messages(df: DLISFile) -> tuple[eflr_types.MessageItem]:
    m = df.add_message(
        name="MESSAGE-1",
        message_type="Command",
        time=datetime(year=2050, month=3, day=4, hour=11, minute=23, second=11),
        borehole_drift=123.34,
        vertical_depth=234.45,
        radial_drift=345.56,
        angular_drift=456.67,
        text=["Test message 11111"]
    )

    return m,


def _add_comments(df: DLISFile) -> tuple[eflr_types.CommentItem, ...]:
    c1 = df.add_comment(
        name="COMMENT-1",
        text=["SOME COMMENT HERE"]
    )

    c2 = df.add_comment(
        name="cmt2",
        text=["some other comment here", "and another comment"]
    )

    return c1, c2


def _add_no_formats(df: DLISFile) -> tuple[eflr_types.NoFormatItem, ...]:
    nf1 = df.add_no_format(
        name="no_format_1",
        consumer_name="SOME TEXT NOT FORMATTED",
        description="TESTING-NO-FORMAT"
    )

    nf2 = df.add_no_format(
        name="no_fmt2",
        consumer_name="xyz",
        description="TESTING NO FORMAT 2"
    )

    return nf1, nf2


def _add_long_name(df: DLISFile) -> eflr_types.LongNameItem:
    ln = df.add_long_name(
        name="LNAME-1",
        general_modifier=["SOME ASCII TEXT"],
        quantity="SOME ASCII TEXT",
        quantity_modifier=["SOME ASCII TEXT"],
        altered_form="SOME ASCII TEXT",
        entity="SOME ASCII TEXT",
        entity_modifier=["SOME ASCII TEXT"],
        entity_number="SOME ASCII TEXT",
        entity_part="SOME ASCII TEXT",
        entity_part_number="SOME ASCII TEXT",
        generic_source="SOME ASCII TEXT",
        source_part=["SOME ASCII TEXT"],
        source_part_number=["SOME ASCII TEXT"],
        conditions=["SOME ASCII TEXT"],
        standard_symbol="SOME ASCII TEXT",
        private_symbol="SOME ASCII TEXT"
    )

    return ln


def _add_groups(df: DLISFile, channels: tuple[eflr_types.ChannelItem, ...],
                processes: tuple[eflr_types.ProcessItem, ...]) -> tuple[eflr_types.GroupItem, ...]:
    g1 = df.add_group(
        name="ChannelGroup",
        description="Group of channels",
        object_type="CHANNEL",
        object_list=[channels[1], channels[2]]
    )

    g2 = df.add_group(
        name="ProcessGroup",
        description="Group of processes",
        object_type="PROCESS",
        object_list=[processes[0], processes[1]]
    )

    g3 = df.add_group(
        name="MultiGroup",
        description="Group of groups",
        object_type="GROUP",
        group_list=[g1, g2]
    )

    return g1, g2, g3


def create_dlis_file_object() -> DLISFile:
    df = DLISFile(storage_unit_label=make_sul(), file_header=make_file_header())
    _add_origin(df)

    axes = _add_axes(df)
    channels = _add_channels(df, axes[0])
    frame = _add_frame(df, *channels[4:9])
    zones = _add_zones(df)
    params = _add_parameters(df, zones)
    equipment = _add_equipment(df)
    tools = _add_tools(df, equipment, params, channels)
    computations = _add_computation(df, axes, zones, tools)
    processes = _add_processes(df, params, channels, computations)
    _add_splices(df, channels, zones)
    _add_calibrations(df, axes, channels, params)
    wrp = _add_well_reference_points(df)
    _add_paths(df, frame, wrp[0], channels)
    _add_messages(df)
    _add_comments(df)
    _add_no_formats(df)
    _add_long_name(df)
    _add_groups(df, channels, processes)

    return df


def write_short_dlis(fname: Union[str, os.PathLike[str]], data: Union[dict, os.PathLike[str], np.ndarray]) -> None:
    df = create_dlis_file_object()
    df.write(fname, data=data)
