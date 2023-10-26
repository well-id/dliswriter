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


class ReprCodeConverter:
    class ReprCodeError(ValueError):
        pass

    float_codes = tuple(code for code in RepresentationCode.__members__.values() if code.value <= 11)
    sint_codes = tuple(code for code in RepresentationCode.__members__.values() if 12 <= code.value <= 14)
    uint_codes = tuple(code for code in RepresentationCode.__members__.values() if 15 <= code.value <= 18)
    int_codes = sint_codes + uint_codes
    numeric_codes = float_codes + int_codes

    # TODO: verify
    numpy_dtypes = {
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

    generic_types = {
        datetime: RepresentationCode.DTIME,
        int: RepresentationCode.SLONG,
        float: RepresentationCode.FDOUBL,
        str: RepresentationCode.ASCII
    }

    @classmethod
    def _determine_repr_code_single(cls, value):
        if isinstance(value, (np.generic, np.ndarray)):
            repr_code = cls.numpy_dtypes.get(value.dtype.name, None)
            if repr_code is None:
                raise cls.ReprCodeError(f"Cannot determine representation code for numpy dtype {value.dtype}")
            return repr_code

        repr_code_getter = cls.generic_types.get(type(value), None)
        if not repr_code_getter:
            raise cls.ReprCodeError(f"Cannot determine representation code for type {type(value)} ({value})")
        return repr_code_getter

    @classmethod
    def _determine_repr_code_multiple(cls, values):
        repr_codes = [cls._determine_repr_code_single(v) for v in values]
        if len(set(repr_codes)) == 1:
            return repr_codes[0]

        if not all(rc in cls.numeric_codes for rc in repr_codes):
            raise cls.ReprCodeError(f"Cannot determine a common representation code for values: {values} "
                                    f"(proposed representation codes are: {repr_codes})")

        # at this stage we know all codes are numeric

        if any(rc in cls.float_codes for rc in repr_codes):
            # if any of them is a float - return the float code
            return RepresentationCode.FDOUBL

        if any(all(rc in codes for rc in repr_codes) for codes in (cls.float_codes, cls.sint_codes, cls.uint_codes)):
            # only floats, only signed ints, or only unsigned ints
            return max(repr_codes)

        if any(rc in cls.sint_codes for rc in repr_codes):
            # if any of them is a signed int - return a signed int code
            return RepresentationCode.SLONG

        raise cls.ReprCodeError(f"Cannot determine a representation code for values: {values}")

    @classmethod
    def determine_repr_code(cls, v):
        if isinstance(v, (list, tuple)):
            return cls._determine_repr_code_multiple(v)
        return cls._determine_repr_code_single(v)
