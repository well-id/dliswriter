import os
from typing import Union
import numpy as np

from dlis_writer.writer.file import DLISFile
from dlis_writer.logical_record import eflr_types
from dlis_writer.logical_record.misc.storage_unit_label import StorageUnitLabel


def _make_origin():
    origin = eflr_types.OriginItem(
        "DEFAULT ORIGIN",
        creation_time="2050/03/02 15:30:00",
        file_id="WELL ID",
        file_set_name="Test file set name",
        file_set_number=1,
        file_number=8,
        run_number=13,
        well_id=5,
        well_name="Test well name",
        field_name="Test field name",
        company="Test company",
    )

    return origin


def _make_file_header():
    return eflr_types.FileHeaderItem("DEFAULT FHLR", sequence_number=1)


def _make_sul():
    return StorageUnitLabel("DEFAULT STORAGE SET", sequence_number=1)


def _add_frame(df, *channels: eflr_types.ChannelItem):
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


def _add_channels(df, ax1):
    ch = df.add_channel(
        name="Some Channel",
        dataset_name="image1",
        long_name="Some not so very long channel name",
        properties="property1, property 2 with multiple words",
        representation_code=2,
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


def _add_axes(df):
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
        coordinates=8,
        spacing=2
    )
    ax2.spacing.units = "m"

    return ax1, ax2


def _add_zones(df):
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

    zx = eflr_types.ZoneItem(
        name="Zone-X",
        description="Zone not added to any parameter",
        domain="TIME",
        maximum=10,
        minimum=1
    )
    zx.maximum.units = "s"
    zx.minimum.units = "s"

    return z1, z2, z3, z4, zx


def _add_parameters(df: DLISFile, zones):
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


def _add_equipment(df: DLISFile):
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
               parameters: tuple[eflr_types.ParameterItem, ...], channels: tuple[eflr_types.ChannelItem, ...]):
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
                   channels: tuple[eflr_types.ChannelItem, ...], computations: tuple[eflr_types.ComputationItem, ...]):
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
                     tools: tuple[eflr_types.ToolItem, ...]):
    c1 = df.add_computation(
        name="COMPT-1",
        long_name="COMPT1",
        properties=["PROP 1", "AVERAGED"],
        dimension=[1],
        axis=axes[0],
        zones=zones[:3],
        values=[100, 200, 300],
        source=tools[0]
    )
    c1.values.representation_code = "UNORM"

    c2 = df.add_computation(
        name="COMPT2",
        long_name="COMPT 2",
        properties=["PROP 2", "AVERAGED"],
        axis=axes[0],
        zones=[zones[0], zones[2]],
        values=[1.5, 2.5]
    )

    cx = df.add_computation(
        name="COMPT-X",
        long_name="Computation not added to process",
        properties=["XYZ"],
        axis=axes[0],
        zones=[zones[2]],
        values=[12],
    )

    return c1, c2, cx


def _add_splices(df: DLISFile, channels, zones):
    s = df.add_splice(
        name="splc1",
        output_channel=channels[6],
        input_channels=[channels[1], channels[2]],
        zones=[zones[0], zones[1]]
    )

    return s,


def create_dlis_file_object():
    df = DLISFile(
        origin=_make_origin(),
        file_header=_make_file_header(),
        storage_unit_label=_make_sul()
    )

    axes = _add_axes(df)
    channels = _add_channels(df, axes[0])
    frame = _add_frame(df, *channels[4:9])
    zones = _add_zones(df)
    params = _add_parameters(df, zones)
    equipment = _add_equipment(df)
    tools = _add_tools(df, equipment, params, channels)
    computations = _add_computation(df, axes, zones, tools)
    processes = _add_processes(df, params, channels, computations)
    splices = _add_splices(df, channels, zones)

    return df


def write_dlis(fname: Union[str, os.PathLike], data: [dict, os.PathLike[str], np.ndarray]):
    df = create_dlis_file_object()
    df.write(fname, data=data)
