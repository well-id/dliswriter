import os
from typing import Union
import numpy as np

from dlis_writer.file import DLISFile

from tests.dlis_files_for_testing.common import make_file_header, make_sul, make_origin


def create_dlis_file_object() -> DLISFile:
    df = DLISFile(
        origin=make_origin(),
        file_header=make_file_header(),
        storage_unit_label=make_sul()
    )

    # define frame 1
    n_rows_1 = 100
    ch_depth_1 = df.add_channel('DEPTH', data=np.arange(n_rows_1), units='m')
    ch_rpm_1 = df.add_channel("RPM", data=10 * np.random.rand(n_rows_1))
    ch_amp_1 = df.add_channel("AMPLITUDE", data=np.random.rand(n_rows_1, 10))
    df.add_frame("FRAME1", channels=(ch_depth_1, ch_rpm_1, ch_amp_1), index_type='BOREHOLE-DEPTH')

    # define frame 2
    n_rows_2 = 200
    ch_depth_2 = df.add_channel('DEPTH', data=np.arange(n_rows_2), units='m')
    ch_rpm_2 = df.add_channel("RPM", data=(np.arange(n_rows_2) % 10).astype(np.int32))
    ch_amp_2 = df.add_channel("AMPLITUDE", data=np.arange(n_rows_2 * 5).reshape(n_rows_2, 5) % 6)
    df.add_frame("FRAME2", channels=(ch_depth_2, ch_rpm_2, ch_amp_2), index_type='BOREHOLE-DEPTH')

    return df


def write_double_frame_dlis(fname: Union[str, os.PathLike[str]]) -> DLISFile:
    df = create_dlis_file_object()
    df.write(fname)

    return df
