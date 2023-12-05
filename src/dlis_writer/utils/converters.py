from datetime import datetime
import numpy as np
from typing import Callable, Any, Iterable

from dlis_writer.utils.enums import RepresentationCode


def get_ascii_bytes(value: str, required_length: int, justify_left: bool = False) -> bytes:
    """Encode a string value as ASCII.

    Args:
        value           :   Value to convert.
        required_length :   Required length of the string. Padding will be added if the original string is shorter.
        justify_left    :   If True, pad with trailing blanks. Otherwise, pad with preceding blanks.

    Returns:
        ASCII encoded bytes.
    """

    lv = len(value)
    if lv > required_length:
        raise ValueError(f"Provided string is too long ({lv} chars) for required length of {required_length}")

    padding = (required_length - lv) * ' '

    if justify_left:
        padded_value = value + padding
    else:
        padded_value = padding + value

    return padded_value.encode('ascii')


def _filter_codes(cond: Callable) -> tuple[RepresentationCode, ...]:
    """Return a tuple containing all representation codes fulfilling a certain condition ('cond')."""

    return tuple(code for code in RepresentationCode.__members__.values() if cond(code))


class ReprCodeConverter:
    """Choose a representation code based on the provided data or determine data type from a representation code."""

    class ReprCodeError(ValueError):
        """Error raised if a representation code for a given value cannot be determined."""

        pass

    float_codes = _filter_codes(lambda code: code.value <= 11)          #: representation codes for floats
    sint_codes = _filter_codes(lambda code: 12 <= code.value <= 14)     #: representation codes for signed ints
    uint_codes = _filter_codes(lambda code: 15 <= code.value <= 18)     #: representation codes for unsigned ints
    int_codes = sint_codes + uint_codes                                 #: representation codes for all integers
    numeric_codes = float_codes + int_codes                             #: representation codes for all numbers

    # mapping of numpy dtype names on corresponding representation codes
    # TODO: verify
    numpy_dtypes: dict[str, RepresentationCode] = {
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

    # mapping of numerical representation codes on corresponding numpy dtypes
    repr_codes_to_numpy_dtypes = {
        RepresentationCode.FDOUBL: np.float64,
        RepresentationCode.FSINGL: np.float32,
        RepresentationCode.USHORT: np.uint16,
        RepresentationCode.UNORM: np.uint32,
        RepresentationCode.ULONG: np.uint64,
        RepresentationCode.SSHORT: np.int8,
        RepresentationCode.SNORM: np.int32,
        RepresentationCode.SLONG: np.int64
    }

    # mapping of different object types on corresponding representation codes
    generic_types: dict[type, RepresentationCode] = {
        datetime: RepresentationCode.DTIME,
        int: RepresentationCode.SLONG,
        float: RepresentationCode.FDOUBL,
        str: RepresentationCode.ASCII
    }

    @classmethod
    def determine_repr_code_from_numpy_dtype(cls, dt: np.dtype) -> RepresentationCode:
        """Determine representation code for a given numpy dtype."""

        repr_code = cls.numpy_dtypes.get(dt.name, None)
        if repr_code is None:
            raise cls.ReprCodeError(f"Cannot determine representation code for numpy dtype {dt}")
        return repr_code

    @classmethod
    def determine_repr_code_from_generic_type(cls, t: type) -> RepresentationCode:
        """Determine representation code for a given type (e.g. int, float, str, etc.)."""

        repr_code = cls.generic_types.get(t, None)
        if not repr_code:
            raise cls.ReprCodeError(f"Cannot determine representation code for type {t}")
        return repr_code

    @classmethod
    def _determine_repr_code_single(cls, value: Any) -> RepresentationCode:
        """Determine representation code for a value (which is not a list/tuple etc., but might be a numpy array)."""

        if isinstance(value, (np.generic, np.ndarray)):
            return cls.determine_repr_code_from_numpy_dtype(value.dtype)
        return cls.determine_repr_code_from_generic_type(type(value))

    @classmethod
    def _determine_repr_code_multiple(cls, values: Iterable[Any]) -> RepresentationCode:
        """Determine representation code for an iterable of values.

        Note:
            A single representation code for all values is returned. In case it is not the same representation code
            for all values, the method will try to find one that fits all the values (e.g. SLONG if some values are
            SLONG and some SNORM, od FDOUBL if all values are numbers). If that's not possible, a ReprCodeError
            is raised.
        """

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
    def determine_repr_code_from_value(cls, v: Any) -> RepresentationCode:
        """Determine representation code for a value.

        In case the value is a list or a tuple, the method will try to find a single representation code which fits
        all elements of the value.
        """

        if isinstance(v, (list, tuple)):
            return cls._determine_repr_code_multiple(v)
        return cls._determine_repr_code_single(v)
