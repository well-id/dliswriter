from functools import lru_cache
from enum import IntEnum

from .custom_types import LogicalRecordType
from .custom_types import LogicalRecordTypeCode
from .enums import RepresentationCode


class LogicalRecordTypeEnum(IntEnum):
    FHLR = 0
    OLR = 1
    AXIS = 2
    CHANNL = 3
    FRAME = 4
    STATIC = 5
    SCRIPT = 6
    UPDATE = 7
    UDI = 8
    LNAME = 9
    SPEC = 10
    DICT = 11

    @classmethod
    def get_all_codes(cls):
        return cls._member_names_


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

    @classmethod
    def get_all_code_names(cls) -> list:
        return cls._member_names_

    @classmethod
    def get_all_code_values(cls) -> list:
        return list(cls._value2member_map_.keys())


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


def get_logical_record_type(logical_record_type: LogicalRecordType) -> LogicalRecordTypeCode:
    """Converts EFLR logical record type which is a string to corresponding int code.

    Args:
        logical_record_type:    One of the EFLR logical record types in RP66 V1

    Returns:
        Corresponding code

    Raises:
        ValueError: If logical_record_type is not one of the types in RP66 V1 spec

    .. _RP66 V1 Appendix A.2:
        http://w3.energistics.org/rp66/v1/rp66v1_appa.html#A_2

    """

    try:
        lrt_code = LogicalRecordTypeEnum[logical_record_type]
    except KeyError:
        error_message = (f'Provided Logical Record Type "{logical_record_type}" could not be found\n'
                         'Description must be exactly one of the following:\n')
        error_message += ''.join('\t' + lrt + '\n' for lrt in LogicalRecordTypeEnum.get_all_codes())
        raise ValueError(error_message)

    return lrt_code


def get_representation_code_value(code: RepresentationCode) -> int:
    """Converts RP66 V1 representation code to corresponding number.

    Args:
        code: One of the representation code names or numbers specified in RP66 V1 Appendix B

    Returns:
        Number corresponding to the given RepresentationCode.

    Raises:
        ValueError: If the provided code name is not found in the code-to-number converter enum.

    Note:
        _RP66 V1 Appendix B Representation Codes: http://w3.energistics.org/rp66/v1/rp66v1_appb.html

    """

    try:
        code_value = RepresentationCodeConversionEnum[code.name]

    except KeyError:
        error_message = (f'Provided representation code "{code.name}" could not be found\n'
                         f'Key must be exactly one of the following:\n')
        error_message += ''.join('\t' + key + '\n' for key in RepresentationCodeConversionEnum.get_all_code_names())
        raise ValueError(error_message)

    return code_value.value


def get_representation_code_from_value(code_value: int) -> RepresentationCode:
    """Converts a number to the corresponding RP66 V1 representation code.

    Args:
        code_value: One of the representation code names or numbers specified in RP66 V1 Appendix B

    Returns:
        The Representation Code corresponding to the given code_value.

    Raises:
        ValueError: If the given number does not correspond to any member of the code-to-number converter enum.

    Note:
        _RP66 V1 Appendix B Representation Codes: http://w3.energistics.org/rp66/v1/rp66v1_appb.html

    """

    try:
        conv_code = RepresentationCodeConversionEnum(code_value)

    except ValueError:
        error_message = f'Provided value "{code_value}" could not be found\nKey must be exactly one of the following:\n'
        error_message += ''.join('\t' + key + '\n' for key in RepresentationCodeConversionEnum.get_all_code_values())
        raise ValueError(error_message)

    return RepresentationCode[conv_code.name]
