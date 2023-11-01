from datetime import datetime
from typing import Any
from functools import lru_cache

from dlis_writer.utils.enums import RepresentationCode


# offsets used in writing structs for UVARI representation code (see '_write_struct_uvari' function)
UNORM_OFFSET = 32768        #: offset added to values packed as UNORM; '10' and 14 zeros
ULONG_OFFSET = 3221225472   #: offset added to values packed as ULONG; 11 and 30 zeros


def _write_struct_dtime(date_time: datetime) -> bytes:
    """Converts datetime object to RP66 V1 DTIME.

    Args:
        date_time: A datetime object.

    Returns:
        RP66 V1 DTIME bytes.

    Quote:
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


    Example:
        >>> from datetime import datetime
        >>> date_time = datetime(2022, 9, 13, 9, 54)
        >>> date_time
        datetime.datetime(2022, 9, 13, 9, 54)
        >>> _write_struct_dtime(date_time)
        b'z\t\r\t6\x00\x00\x00'

    .. _RP66 V1 Appendix B.21:
        http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_21

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


def _write_struct_ascii(value):
    value = str(value)
    return _write_struct_uvari(len(value)) + value.encode('ascii')


def _write_struct_uvari(value):
    if value < 128:
        return RepresentationCode.USHORT.converter.pack(value)

    if value < 16384:
        return RepresentationCode.UNORM.converter.pack(value + UNORM_OFFSET)

    # >= 16384
    return RepresentationCode.ULONG.converter.pack(value + ULONG_OFFSET)


def _write_struct_ident(value):
    value = str(value)
    return RepresentationCode.USHORT.converter.pack(len(value)) + value.encode('ascii')


def _write_struct_obname(value):
    try:
        origin_reference = _write_struct_uvari(value.origin_reference)
        copy_number = RepresentationCode.USHORT.converter.pack(value.copy_number)
        name = _write_struct_ident(value.name)

        obname = origin_reference + copy_number + name

    except AttributeError:
        raise TypeError(f"'OBNAME' struct can only be written for an EFLR object or a FileHeader; "
                        f"got {type(value)}: {value}")

    return obname


def _write_struct_objref(value):
    return _write_struct_ident(value.set_type) + value.obname


def _write_struct_status(value):
    if not (value == 0 or value == 1):
        raise ValueError("\nSTATUS must be 1 or 0\n1 indicates: ALLOWED"
                         " / TRUE / ON\n0 indicates: DISALLOWED / FALSE / OFF")

    return RepresentationCode.USHORT.converter.pack(value)


_struct_dict = {
    RepresentationCode.ASCII: _write_struct_ascii,
    RepresentationCode.UVARI: _write_struct_uvari,
    RepresentationCode.IDENT: _write_struct_ident,
    RepresentationCode.DTIME: _write_struct_dtime,
    RepresentationCode.OBNAME: _write_struct_obname,
    RepresentationCode.OBJREF: _write_struct_objref,
    RepresentationCode.STATUS: _write_struct_status
}


@lru_cache(maxsize=65536)
def write_struct(representation_code: RepresentationCode, value: Any) -> bytes:
    """Converts the value to bytes according to the RP66 V1 spec.

    Args:
        representation_code: One of the representation codes from struct_type_dict.keys()
        value: Could be a list, tuple, int, EFLR object, etc.

    Returns:
        Value converted to bytes depending on representation_code and RP66 V1 spec.

    Raises:
        Exception: If representation_code is STATUS and value is not 1 or 0. 

    """

    func = _struct_dict.get(representation_code, None)
    if func:
        return func(value)

    return representation_code.converter.pack(value)
