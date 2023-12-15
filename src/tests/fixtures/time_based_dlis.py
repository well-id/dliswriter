import os
from typing import Union
import numpy as np

from tests.fixtures.common import make_dlis_file_base


def create_dlis_file_object():
    df = make_dlis_file_base()

    return df


def write_time_based_dlis(fname: Union[str, os.PathLike], data: [dict, os.PathLike[str], np.ndarray]):
    df = create_dlis_file_object()
    df.write(fname, data=data)
