from functools import lru_cache
from enum import IntEnum

from dlis_writer.utils.enums import RepresentationCode


class RepresentationCodeConversionEnum(IntEnum):
    FSHORT = 1
    FSINGL = 2
    FSING1 = 3
    FSING2 = 4
    ISINGL = 5
    VSINGL = 6
    FDOUBL = 7
    FDOUB1 = 8
    FDOUB2 = 9
    CSINGL = 10
    CDOUBL = 11
    SSHORT = 12
    SNORM = 13
    SLONG = 14
    USHORT = 15
    UNORM = 16
    ULONG = 17
    UVARI = 18
    IDENT = 19
    ASCII = 20
    DTIME = 21
    ORIGIN = 22
    OBNAME = 23
    OBJREF = 24
    ATTREF = 25
    STATUS = 26
    UNITS = 27


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


def get_representation_code_value(code: RepresentationCode) -> int:
    """Converts RP66 V1 representation code to corresponding number.

    Args:
        code: One of the representation code names or numbers specified in RP66 V1 Appendix B

    Returns:
        Number corresponding to the given RepresentationCode.

    Note:
        _RP66 V1 Appendix B Representation Codes: http://w3.energistics.org/rp66/v1/rp66v1_appb.html

    """

    return RepresentationCodeConversionEnum[code.name].value


def get_representation_code_from_value(code_value: int) -> RepresentationCode:
    """Converts a number to the corresponding RP66 V1 representation code.

    Args:
        code_value: One of the representation code names or numbers specified in RP66 V1 Appendix B

    Returns:
        The Representation Code corresponding to the given code_value.

    Note:
        _RP66 V1 Appendix B Representation Codes: http://w3.energistics.org/rp66/v1/rp66v1_appb.html

    """

    return RepresentationCode[RepresentationCodeConversionEnum(code_value).name]
