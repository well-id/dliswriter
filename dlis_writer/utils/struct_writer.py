from datetime import datetime
from typing import Any, TYPE_CHECKING
from functools import lru_cache

from dlis_writer.utils.enums import RepresentationCode

if TYPE_CHECKING:
    from dlis_writer.logical_record.core.eflr import EFLRObject


# offsets used in writing structs for UVARI representation code (see '_write_struct_uvari' function)
UNORM_OFFSET = 32768        #: offset added to values packed as UNORM; '10' and 14 zeros
ULONG_OFFSET = 3221225472   #: offset added to values packed as ULONG; 11 and 30 zeros


def _write_struct_dtime(date_time: datetime) -> bytes:
    """Convert a datetime object to bytes according to the RP66 V1 standard.

    Args:
        date_time: The datetime object to be converted.

    Returns:
        Bytes representing the date time.

    From RP66:
        Y = Years Since 1900 (Range 0 to 255)
        TZ = Time Zone (0 = Local Standard, 1 = Local Daylight Savings, 2 = Greenwich Mean Time)
        M = Month of the Year (Range 1 to 12)
        D = Day of Month (Range 1 to 31)
        H = Hours Since Midnight (Range 0 to 23)
        MN = Minutes Past Hour (Range 0 to 59)
        S = Seconds Past Minute (Range 0 to 59)
        MS = Milliseconds Past Second (Range 0 to 999)

        9:20:15.62 PM, April 19, 1987 (DST) =
        87 years since 1900, 4th month, 19th day,
        21 hours since midnight, 20 minutes past hour,
        15 seconds past minute, 620 milliseconds past second =
            01010111 00010100 00010011 00010101
            00010100 00001111 00000010 01101100

    """
    
    value = b''

    time_zone = '{0:04b}'.format(0)  # Local Standard Time is set as default
    month = '{0:04b}'.format(date_time.month)

    value += RepresentationCode.USHORT.converter.pack(date_time.year - 1900)
    value += RepresentationCode.USHORT.converter.pack(int(time_zone + month, 2))
    value += RepresentationCode.USHORT.converter.pack(date_time.day)
    value += RepresentationCode.USHORT.converter.pack(date_time.hour)
    value += RepresentationCode.USHORT.converter.pack(date_time.minute)
    value += RepresentationCode.USHORT.converter.pack(date_time.second)
    value += RepresentationCode.UNORM.converter.pack(date_time.microsecond // 1000)
    
    return value


def _write_struct_ascii(value: Any) -> bytes:
    """Convert value to str, encode as ASCII, and represent as bytes.

    The first bytes are the number of characters in the value (converted to str).
    """

    value = str(value)
    return _write_struct_uvari(len(value)) + value.encode('ascii')


def _write_struct_uvari(value: int) -> bytes:
    """Convert an integer to bytes. The format (USHORT/UNORM/ULONG) is chosen depending on the provided value."""

    if value < 128:
        return RepresentationCode.USHORT.converter.pack(value)

    if value < 16384:
        return RepresentationCode.UNORM.converter.pack(value + UNORM_OFFSET)

    # >= 16384
    return RepresentationCode.ULONG.converter.pack(value + ULONG_OFFSET)


def _write_struct_obname(value: "EFLRObject") -> bytes:
    """Create a reference to an EFLRObject, based on the object's name."""

    if value.origin_reference is None:
        raise RuntimeError(f"Origin reference of {value} has not been specified")

    try:
        origin_reference = _write_struct_uvari(value.origin_reference)
        copy_number = RepresentationCode.USHORT.converter.pack(value.copy_number)
        name = _write_struct_ascii(value.name)

        obname = origin_reference + copy_number + name

    except AttributeError:
        raise TypeError(f"'OBNAME' struct can only be written for an EFLR object; got {type(value)}: {value}")

    return obname


def _write_struct_objref(value: "EFLRObject") -> bytes:
    """Create a reference to an EFLRObject, based on the object's name and set type it belongs to."""

    return _write_struct_ascii(value.parent.set_type) + value.obname


def _write_struct_status(value: int) -> bytes:
    """Represent status (1 or 0) as bytes."""

    if value != 0 and value != 1:
        raise ValueError(f"STATUS must be 1 (meaning ALLOWED/TRUE/ON) or 0 (meaning DISALLOWED/FALSE/OFF); got {value}")

    return RepresentationCode.USHORT.converter.pack(value)


# dictionary collecting all the individual write_struct sub-functions for faster access in the main function below
_struct_dict = {
    RepresentationCode.ASCII: _write_struct_ascii,
    RepresentationCode.UVARI: _write_struct_uvari,
    RepresentationCode.IDENT: _write_struct_ascii,
    RepresentationCode.DTIME: _write_struct_dtime,
    RepresentationCode.OBNAME: _write_struct_obname,
    RepresentationCode.OBJREF: _write_struct_objref,
    RepresentationCode.STATUS: _write_struct_status
}


@lru_cache(maxsize=65536)
def write_struct(representation_code: RepresentationCode, value: Any) -> bytes:
    """Convert a value to bytes according to the RP66 V1 spec.

    Args:
        representation_code :   The way the value should be represented as.
        value               :   Value to be converted.

    Returns:
        Value converted to bytes depending on representation_code and RP66 V1 spec.
    """

    func = _struct_dict.get(representation_code, None)  # get a converter corresponding to the repr code
    if func:
        return func(value)

    return representation_code.converter.pack(value)  # if no converter was found, use the one built in the enum
