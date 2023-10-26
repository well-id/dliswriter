from functools import lru_cache
from datetime import datetime

import numpy as np

from dlis_writer.utils.enums import RepresentationCode


@lru_cache(maxsize=4096)
def get_ascii_bytes(value: str, required_length: int, justify_left: bool = False) -> bytes:
    """Special method used for Storage Unit Label.

    Args:
        value:              Value to convert to ascii bytes
        required_length:    Specified ascii string length
        justify_left:       When the length of the value is less than required length,
                                trailing or preceding blanks/zeros is required depending on the data type.
                                The default behaviour (flag set to False) is justifying the value to the right
                                and filling the remaining required characters with PRECEDING "blanks".
                                Setting the flag to True adds TRAILING blanks.

    Returns:
        ASCII encoded bytes.
    """

    if justify_left:
        return (str(value) + (required_length - len(str(value))) * ' ').encode('ascii')
    return ((required_length - len(str(value))) * ' ' + str(value)).encode('ascii')


# TODO: verify
numpy_dtype_converter = {
    'int_': RepresentationCode.SLONG,
    'int8': RepresentationCode.SSHORT,
    'int16': RepresentationCode.SNORM,
    'int32': RepresentationCode.SNORM,
    'int64': RepresentationCode.SLONG,
    'uint8': RepresentationCode.USHORT,
    'uint16': RepresentationCode.USHORT,
    'uint32': RepresentationCode.UNORM,
    'uint64': RepresentationCode.ULONG,
    'float_': RepresentationCode.FDOUBL,
    'float16': RepresentationCode.FSINGL,
    'float32': RepresentationCode.FSINGL,
    'float64': RepresentationCode.FDOUBL
}


int_short_bound = 2**8
int_norm_bound = 2**32


def _get_repr_code_for_integer(v):
    if -int_short_bound <= v <= int_short_bound-1:
        return RepresentationCode.SSHORT
    if -int_norm_bound <= v <= int_norm_bound-1:
        return RepresentationCode.SNORM
    return RepresentationCode.SLONG


def _get_repr_code_for_float(v):
    return RepresentationCode.FDOUBL


generic_type_converter = {
    datetime: lambda v: RepresentationCode.DTIME,
    int: _get_repr_code_for_integer,
    float: _get_repr_code_for_float,
    str: lambda v: RepresentationCode.ASCII
}


def determine_repr_code(value):
    if isinstance(value, (np.generic, np.ndarray)):
        repr_code = numpy_dtype_converter.get(value.dtype.name, None)
        if repr_code is None:
            raise ValueError(f"Cannot determine representation code for numpy dtype {value.dtype}")
        return repr_code

    repr_code_getter = generic_type_converter.get(type(value), None)
    if not repr_code_getter:
        raise ValueError(f"Cannot determine representation code for type {type(value)} ({value})")
    return repr_code_getter(value)

