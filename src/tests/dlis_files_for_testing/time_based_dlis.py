import os
from typing import Union
import numpy as np

from dlis_writer.writer.file import DLISFile
from dlis_writer.logical_record import eflr_types

from tests.dlis_files_for_testing.common import make_file_header, make_sul, make_origin


def _add_channels(df: DLISFile):
    ch_time = df.add_channel(
        name="posix time",
        dataset_name="/contents/time",
        units="s",
        representation_code=7,
        dimension=[1]
    )

    ch_rpm = df.add_channel(
        name="surface rpm",
        dataset_name="contents/rpm",
        representation_code=7
    )

    ch_amp = df.add_channel(
        name="amplitude",
        dataset_name="contents/image0",
        representation_code=2
    )

    ch_radius = df.add_channel(
        name="radius",
        dataset_name="/contents/image1",
        dimension=[128],
        units="in",
        representation_code="FSINGL"
    )

    ch_radius_pooh = df.add_channel(
        name="radius_pooh",
        dataset_name="contents/image2",
        dimension=[128],
        units="m",
        representation_code=2
    )

    return ch_time, ch_rpm, ch_amp, ch_radius, ch_radius_pooh


def _add_frame(df: DLISFile, channels: tuple[eflr_types.ChannelItem, ...]):
    fr = df.add_frame(
        name="MAIN",
        index_type="TIME",
        channels=channels
    )

    fr.spacing.units = "s"
    fr.spacing.representation_code = "FDOUBL"
    fr.index_max.representation_code = "FDOUBL"
    fr.index_min.representation_code = "FDOUBL"

    return fr


def create_dlis_file_object():
    df = DLISFile(
        origin=make_origin(),
        file_header=make_file_header(),
        storage_unit_label=make_sul()
    )

    channels = _add_channels(df)
    _add_frame(df, channels)

    return df


def write_time_based_dlis(fname: Union[str, os.PathLike], data: [dict, os.PathLike[str], np.ndarray], **kwargs):
    df = create_dlis_file_object()
    df.write(fname, data=data, **kwargs)
