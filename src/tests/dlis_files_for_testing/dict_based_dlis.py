import os
from typing import Union

from dlis_writer.file import DLISFile
from dlis_writer.logical_record import eflr_types

from tests.dlis_files_for_testing.common import make_file_header, make_sul, make_origin


def _add_channels(df: DLISFile, data_dict: dict) -> tuple[eflr_types.ChannelItem, ...]:
    channels = []
    for key, value in data_dict.items():
        ch = df.add_channel(
            name=key,
            data=value
        )
        channels.append(ch)

    return tuple(channels)


def write_dict_based_dlis(fname: Union[str, os.PathLike[str]], data_dict: dict) -> None:
    df = DLISFile(
        origin=make_origin(),
        file_header=make_file_header(),
        storage_unit_label=make_sul()
    )

    channels = _add_channels(df, data_dict=data_dict)
    df.add_frame("MAIN", index_type="DEPTH", channels=channels)

    df.write(fname)
