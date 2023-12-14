from datetime import datetime, timedelta
import numpy as np

from dlis_writer.writer.file import DLISFile
from dlis_writer.logical_record import eflr_types
from dlis_writer.logical_record.misc.storage_unit_label import StorageUnitLabel
from dlis_writer.utils.enums import RepresentationCode


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
        source="some source",
        minimum_value=0,
        maximum_value=127.6,
    )

    ch1 = df.add_channel(
        name="Channel 1",
        dimension=[10, 10],
        units="in"
    )

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
        "Axis - X",
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
    
    return df


def write_dlis(fname):
    df = create_dlis_file_object()
    df.write(fname)
