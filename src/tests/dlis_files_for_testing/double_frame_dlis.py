import os
from typing import Union

from dliswriter.file import DLISFile
from dliswriter.utils.enums import FrameIndexType

from tests.dlis_files_for_testing.common import make_df


def _define_frame_from_data(df: DLISFile, name: str, data: dict) -> None:
    ax = df.add_axis("AXIS")

    channels = []
    for i, (ch_name, ch_data) in enumerate(data.items()):
        ch = df.add_channel(ch_name, data=ch_data)
        if not i:
            ch.axis.value = ax
        channels.append(ch)

    df.add_frame(name, channels=channels, index_type=FrameIndexType.BOREHOLE_DEPTH)


def create_dlis_file_object(*data_dicts: dict) -> DLISFile:
    df = make_df()

    for i, d in enumerate(data_dicts):
        _define_frame_from_data(df, f'FRAME{i+1}', d)

    return df


def write_double_frame_dlis(fname: Union[str, os.PathLike[str]], *frame_data: dict) -> DLISFile:
    df = create_dlis_file_object(*frame_data)
    df.write(fname)

    return df
