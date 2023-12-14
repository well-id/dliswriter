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


def _add_frame(*channels: eflr_types.ChannelItem):
    return eflr_types.FrameItem(
        "MAIN FRAME",
        channels=channels,
        **{
            'index_type': 'TIME',
            'spacing.value': 0.5,
            'spacing.units': 's',
            'encrypted': 1,
            'description.value': "Frame description"
        }
    )


def _add_channels(ax1):
    ch = eflr_types.ChannelItem(
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

    ch1 = eflr_types.ChannelItem(
        name="Channel 1",
        dimension=[10, 10],
        units="in"
    )

    ch2 = eflr_types.ChannelItem("Channel 2")
    ch3 = eflr_types.ChannelItem("Channel 13", dataset_name='amplitude', element_limit=128)
    ch_time = eflr_types.ChannelItem("posix time", dataset_name="contents/time", units="s")
    ch_rpm = eflr_types.ChannelItem("surface rpm", dataset_name="contents/rpm")
    ch_amplitude = eflr_types.ChannelItem("amplitude", dataset_name="contents/image0", dimension=128)
    ch_radius = eflr_types.ChannelItem("radius", dataset_name="contents/image1", dimension=128, units="in")
    ch_radius_pooh = eflr_types.ChannelItem("radius_pooh", dataset_name="contents/image2", units="m")
    ch_x = eflr_types.ChannelItem("channel_x", long_name="Channel not added to the frame",
                                  dataset_name="image2", units="s")

    return ch, ch1, ch2, ch3, ch_time, ch_rpm, ch_amplitude, ch_radius, ch_radius_pooh, ch_x


def _add_axes():

    ax1 = eflr_types.AxisItem(
        name="Axis-1",
        axis_id="First axis",
        coordinates=[40.395241, 27.792471],
        spacing=0.33,
        **{'spacing.units': "m"}
    )

    ax2 = eflr_types.AxisItem(
        "Axis - X",
        axis_id="Axis not added to computation",
        **{
            "coordinates.value": 8,
            "spacing.value": 2,
            "spacing.units": "m",
        }
    )

    return ax1, ax2


def create_dlis_file_object():

    df = DLISFile(
        origin=_make_origin(), 
        file_header=_make_file_header(),
        storage_unit_label=_make_sul()
    )

    axes = _add_axes()
    channels = _add_channels(axes[0])
    frame = _add_frame(*channels[:-1])
    
    return df


def write_dlis(fname):
    df = create_dlis_file_object()
    df.write(fname)
