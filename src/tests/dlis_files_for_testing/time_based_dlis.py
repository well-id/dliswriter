import os
from typing import Union, Any
import numpy as np

from dliswriter.file import DLISFile
from dliswriter.logical_record import eflr_types
from dliswriter.utils.enums import Unit

from tests.dlis_files_for_testing.common import make_df


def _add_channels(df: DLISFile, lf: int) -> tuple[eflr_types.ChannelItem, ...]:
    ch_time = df.logical_files[lf].add_channel(
        name="posix time",
        dataset_name="/contents/time",
        units=Unit.SECOND,
        cast_dtype=np.float64,
        dimension=[1],
    )

    ch_rpm = df.logical_files[lf].add_channel(
        name="surface rpm",
        dataset_name="contents/rpm",
        cast_dtype=np.float64,
    )

    ch_amp = df.logical_files[lf].add_channel(
        name="amplitude", dataset_name="contents/image0", cast_dtype=np.float32
    )

    ch_radius = df.logical_files[lf].add_channel(
        name="radius",
        dataset_name="/contents/image1",
        dimension=[128],
        units=Unit.INCH,
        cast_dtype=np.float32,
    )

    ch_radius_pooh = df.logical_files[lf].add_channel(
        name="radius_pooh",
        dataset_name="contents/image2",
        dimension=[128],
        units="m",
        cast_dtype=np.float32,
    )

    return ch_time, ch_rpm, ch_amp, ch_radius, ch_radius_pooh


def _add_frame(
    df: DLISFile, lf: int, channels: tuple[eflr_types.ChannelItem, ...]
) -> eflr_types.FrameItem:
    fr = df.logical_files[lf].add_frame(
        name="MAIN", index_type="TIME", channels=channels
    )

    fr.spacing.units = "s"

    return fr


def create_dlis_file_object() -> DLISFile:
    df = make_df()

    logical_file_index = 0
    channels = _add_channels(df, logical_file_index)
    _add_frame(df, logical_file_index, channels)

    return df


def write_time_based_dlis(
    fname: Union[str, os.PathLike[str]],
    data: Union[dict, os.PathLike[str], np.ndarray],
    **kwargs: Any,
) -> None:
    df = create_dlis_file_object()
    df.write(fname, data=data, **kwargs)
