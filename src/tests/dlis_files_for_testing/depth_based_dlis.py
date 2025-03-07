import os
from typing import Union
import numpy as np

from dliswriter.file import DLISFile
from dliswriter.logical_record import eflr_types
from dliswriter.utils.enums import Unit

from tests.dlis_files_for_testing.common import make_df


def _add_channels(
    df: DLISFile, lf: int
) -> tuple[eflr_types.ChannelItem, eflr_types.ChannelItem]:
    ch_depth = df.logical_files[lf].add_channel(
        name="depth",
        dataset_name="/contents/depth",
        units=Unit.METER,
        cast_dtype=np.float64,
    )

    ch_rpm = df.logical_files[lf].add_channel(
        name="surface rpm",
        dataset_name="contents/rpm",
        cast_dtype=np.float64,
        dimension=[1],
    )

    return ch_depth, ch_rpm


def _add_frame(
    df: DLISFile, lf: int, channels: tuple[eflr_types.ChannelItem, ...]
) -> eflr_types.FrameItem:
    fr = df.logical_files[lf].add_frame(
        name="MAIN", index_type="DEPTH", channels=channels
    )

    fr.spacing.units = "m"

    return fr


def create_dlis_file_object() -> DLISFile:
    df = make_df()

    logical_file_index = 0
    channels = _add_channels(df, logical_file_index)
    _add_frame(df, logical_file_index, channels)

    return df


def write_depth_based_dlis(
    fname: Union[str, os.PathLike[str]], data: Union[dict, os.PathLike[str], np.ndarray]
) -> None:
    df = create_dlis_file_object()
    df.write(fname, data=data)
