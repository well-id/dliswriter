import os
from typing import Union

from dlis_writer.file import DLISFile

from tests.dlis_files_for_testing.common import make_file_header, make_sul, make_origin


def _define_frame_from_data(df: DLISFile, name: str, data: dict):
    channels = []
    for ch_name, ch_data in data.items():
        ch = df.add_channel(ch_name, data=ch_data)
        channels.append(ch)

    df.add_frame(name, channels=channels, index_type='BOREHOLE-DEPTH')


def create_dlis_file_object(*data_dicts) -> DLISFile:
    df = DLISFile(
        origin=make_origin(),
        file_header=make_file_header(),
        storage_unit_label=make_sul()
    )

    for i, d in enumerate(data_dicts):
        _define_frame_from_data(df, f'FRAME{i+1}', d)

    return df


def write_double_frame_dlis(fname: Union[str, os.PathLike[str]], *frame_data: dict) -> DLISFile:
    df = create_dlis_file_object(*frame_data)
    df.write(fname)

    return df
