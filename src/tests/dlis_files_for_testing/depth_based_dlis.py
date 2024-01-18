import os
from typing import Union
import numpy as np

from dlis_writer.file import DLISFile
from dlis_writer.logical_record import eflr_types

from tests.dlis_files_for_testing.common import make_file_header, make_sul, make_origin


def _add_channels(df: DLISFile) -> tuple[eflr_types.ChannelItem, eflr_types.ChannelItem]:
    ch_depth = df.add_channel(
        name="depth",
        dataset_name="/contents/depth",
        units="m",
        cast_dtype=np.float64
    )

    ch_rpm = df.add_channel(
        name="surface rpm",
        dataset_name="contents/rpm",
        cast_dtype=np.float64,
        dimension=[1]
    )

    return ch_depth, ch_rpm


def _add_frame(df: DLISFile, channels: tuple[eflr_types.ChannelItem, ...]) -> eflr_types.FrameItem:
    fr = df.add_frame(
        name="MAIN",
        index_type="DEPTH",
        channels=channels
    )

    fr.spacing.units = "m"

    return fr


def create_dlis_file_object() -> DLISFile:
    df = DLISFile(
        origin=make_origin(),
        file_header=make_file_header(),
        storage_unit_label=make_sul()
    )

    channels = _add_channels(df)
    _add_frame(df, channels)

    return df


def write_depth_based_dlis(fname: Union[str, os.PathLike[str]], data: Union[dict, os.PathLike[str], np.ndarray])\
        -> None:
    df = create_dlis_file_object()
    df.write(fname, data=data)
