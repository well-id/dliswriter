import os
from typing import Union
import numpy as np

from dlis_writer.file import DLISFile
from dlis_writer.logical_record import eflr_types

from tests.dlis_files_for_testing.common import make_file_header, make_sul, make_origin


def _add_channels(df: DLISFile):
    ch_depth = df.add_channel(
        name="depth",
        dataset_name="/contents/depth",
        units="m",
        representation_code="FDOUBL"
    )

    ch_rpm = df.add_channel(
        name="surface rpm",
        dataset_name="contents/rpm",
        representation_code=7,
        dimension=[1]
    )

    return ch_depth, ch_rpm


def _add_frame(df: DLISFile, channels: tuple[eflr_types.ChannelItem, ...]):
    fr = df.add_frame(
        name="MAIN",
        index_type="DEPTH",
        channels=channels
    )

    fr.spacing.units = "m"
    fr.spacing.representation_code = 7      # type: ignore  # using converter associated with the property
    fr.index_max.representation_code = 7    # type: ignore  # using converter associated with the property
    fr.index_min.representation_code = 7    # type: ignore  # using converter associated with the property

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


def write_depth_based_dlis(fname: Union[str, os.PathLike[str]], data: Union[dict, os.PathLike[str], np.ndarray]):
    df = create_dlis_file_object()
    df.write(fname, data=data)
