import re
from datetime import datetime
from typing import Any
from functools import lru_cache

from .enums import RepresentationCode


NOT_TEMPLATE = [
    'origin_reference',
    'copy_number',
    'object_name',
    'logical_record_type',
    'segment_length',
    'is_eflr',
    'has_predecessor_segment',
    'has_successor_segment',
    'is_encrypted',
    'has_encryption_protocol',
    'has_checksum',
    'has_trailing_length',
    'has_padding',
    'set_type',
    'set_name',
    'attributes',
    'bytes',
    'is_dictionary_controlled',
    'dictionary_controlled_objects',
    'split_size',
    'vr_dict',
    'data'
]
"""list: A list of attributes to be neglected while creating Attribute instances for EFLR objects.

When creating attributes for EFLR objects, __dict__ is used to get a list of all attributes.
And for each element in that list, an instance of Attribute class is created. NOT_TEMPLATE
is a list of attributes that won't be in the Template and so neglected when creating Attribute
instances.
"""


def validate_units(value: str) -> str:
    """Validates the user input for UNITS data type according to RP66 V1 specifications.

    Args:
        value: A string representing measurement units provided by the user.

    Returns:
        Value itself if regex check is successful.

    Raises:
        Exception: If the value provided does not fit with RP66 V1 specification.

    

    Quote:
        Syntactically, Representation Code UNITS is similar to Representation Codes IDENT and ASCII.
        However, upper case and lower case are considered
        distinct (e.g., "A" and "a" for Ampere and annum, respectively),
        and permissible characters are restricted to the following ASCII codes:

            --> lower case letters [a, b, c, ..., z]
            --> upper case letters [A, B, C, ..., Z]
            --> digits [0, 1, 2, ..., 9]
            --> blank [ ]
            --> hyphen or minus sign [-]
            --> dot or period [.]
            --> slash [/]
            --> parentheses [(, )]

    

    .. _RP66 V1 Appendix B.27:
        http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_27

    """
    
    regex_checked = ''.join(re.findall(r'[a-zA-Z\d\s\-.,/()]', value))

    if regex_checked == value:
        return value
    else:
        message = '''{}

        \n
        UNITS must comply with the RP66 V1 specification.

        Value "{}" does not comply with the rules printed above.
        '''.format(validate_units.__doc__, value)
        raise Exception(message)


def get_datetime(date_time: datetime) -> bytes:
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
        >>> get_datetime(date_time)
        b'z\t\r\t6\x00\x00\x00'

    .. _RP66 V1 Appendix B.21:
        http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_21

    """
    
    value = b''

    time_zone = '{0:04b}'.format(0) # Local Standard Time is set as default
    month = '{0:04b}'.format(date_time.month)

    value += write_struct(RepresentationCode.USHORT, date_time.year - 1900)
    value += write_struct(RepresentationCode.USHORT, int(time_zone + month, 2))
    value += write_struct(RepresentationCode.USHORT, date_time.day)
    value += write_struct(RepresentationCode.USHORT, date_time.hour)
    value += write_struct(RepresentationCode.USHORT, date_time.minute)
    value += write_struct(RepresentationCode.USHORT, date_time.second)
    value += write_struct(RepresentationCode.UNORM, int(date_time.microsecond / 1000))
    
    return value


def read_struct(representation_code: RepresentationCode, packed_value: bytes) -> Any:
    """Reads bytes and unpacks according to the struct type.

    Args:
        representation_code: One of the representation codes from struct_type_dict.keys()
        packed_value: Bytes as the same size with the representation_code.size

    Returns:
        Unpacked struct value. Might be int, float, str depending on the representation_code.
    """
    return representation_code.value.unpack(packed_value)[0]


def _write_struct_ascii(value):
    return write_struct(RepresentationCode.UVARI, len(str(value))) + str(value).encode('ascii')


def _write_struct_uvari(value):
    if value > 127:
        if value > 16383:
            value = '{0:08b}'.format(value)
            value = '11' + (30 - len(value)) * '0' + value
            return RepresentationCode.ULONG.value.pack(int(value, 2))
        else:
            value = '{0:08b}'.format(value)
            value = '10' + (14 - len(value)) * '0' + value
            return RepresentationCode.UNORM.value.pack(int(value, 2))

    return write_struct(RepresentationCode.USHORT, int('{0:08b}'.format(value), 2))


def _write_struct_ident(value):
    return write_struct(RepresentationCode.USHORT, len(str(value))) + str(value).encode('ascii')


def _write_struct_dtime(value):
    return get_datetime(value)


def _write_struct_obname(value):
    try:
        origin_reference = write_struct(RepresentationCode.UVARI, value[0])
        copy_number = write_struct(RepresentationCode.USHORT, value[1])
        name = write_struct(RepresentationCode.IDENT, value[2])

        obname = origin_reference + copy_number + name

    except TypeError:
        if type(value) == list or type(value) == tuple:
            obname = b''
            for val in value:
                obname += val.obname
        else:
            obname = value.obname

    return obname


def _write_struct_units(value):
    return write_struct(RepresentationCode.IDENT, validate_units(value))


def _write_struct_objref(value):
    return write_struct(RepresentationCode.IDENT, value.set_type) + value.obname


def _write_struct_status(value):
    if value not in [0, 1]:
        error_message = ("\nSTATUS must be 1 or 0\n1 indicates: ALLOWED"
                         " / TRUE / ON\n0 indicates: DISALLOWED / FALSE / OFF")
        raise Exception(error_message)

    return write_struct(RepresentationCode.USHORT, value)


def _write_struct_default(representation_code, value):
    return representation_code.value.pack(value)


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

    if representation_code == RepresentationCode.ASCII:
        return _write_struct_ascii(value)

    elif representation_code == RepresentationCode.UVARI:
        return _write_struct_uvari(value)
    
    elif representation_code == RepresentationCode.IDENT:
        return _write_struct_ident(value)

    elif representation_code == RepresentationCode.DTIME:
        return _write_struct_dtime(value)

    elif representation_code == RepresentationCode.OBNAME:
        return _write_struct_obname(value)

    elif representation_code == RepresentationCode.UNITS:
        return _write_struct_units(value)

    elif representation_code == RepresentationCode.OBJREF:
        return _write_struct_objref(value)

    elif representation_code == RepresentationCode.STATUS:
        return _write_struct_status(value)

    else:
        return _write_struct_default(representation_code, value)


def write_absent_attribute() -> bytes:
    """Returns absent attribute bytes as per RP66 V1 spec"""
    return b'\x00'