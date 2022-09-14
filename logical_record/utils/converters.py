import struct
from typing import Union
from .custom_types import Justify
from .custom_types import LogicalRecordType
from .custom_types import LogicalRecordTypeCode
from .custom_types import RepresentationCode
from .custom_types import RepresentationCodeNumber


def get_ascii_bytes(value: str, required_length: int, justify: Justify=None) -> bytes:
    """Special method used for Storage Unit Label.

    Args:
        value: Value to convert to ascii bytes
        required_length: Specified ascii string length
        justify: When the length of the value is less than required length,
            trailing or preciding blanks/zeros is required depending on the data type.
            The default value is None which equals to justifying the value to the right and
            and filling the remaining required characters with PRECIDING "blanks".
            justify="left" adds TRAILING blanks

    Returns:
        ASCII encoded bytes.

    """

    if justify == 'left':
        return (str(value) + (required_length - len(str(value))) * ' ').encode('ascii')
    return ((required_length - len(str(value))) * ' ' + str(value)).encode('ascii')


def get_logical_record_type(logical_record_type: LogicalRecordType) -> LogicalRecordTypeCode:
    """Converts EFLR logical record type which is a string to corresponding int code.

    Args:
        logical_record_type: One of the EFLR logical record types in RP66 V1

    Returns:
        Corresponding code

    Raises:
        Exception: If logical_record_type is not one of the types in RP66 V1 spec

    .. _RP66 V1 Appendix A.2:
        http://w3.energistics.org/rp66/v1/rp66v1_appa.html#A_2

    """

    logical_record_type_dictionary = {
        'FHLR': 0,
        'OLR': 1,
        'AXIS': 2,
        'CHANNL': 3,
        'FRAME': 4,
        'STATIC': 5,
        'SCRIPT': 6,
        'UPDATE': 7,
        'UDI': 8,
        'LNAME': 9,
        'SPEC': 10,
        'DICT': 11
    }


    if logical_record_type not in list(logical_record_type_dictionary.keys()):

        error_message = (f'Provided Logical Record Type "{logical_record_type}" could not be found\n'
                         'Description must be exactly one of the following:\n')
        error_message += ''.join(['\t' + logical_record_type + '\n' \
                                  for logical_record_type in list(logical_record_type_dictionary.keys())])
        raise Exception(error_message)

    return logical_record_type_dictionary[logical_record_type]


def get_representation_code(key: Union[RepresentationCode, RepresentationCodeNumber],
                            from_value:bool=False) -> Union[RepresentationCodeNumber, RepresentationCode]:
    """Converts RP66 V1 representation code to corresponding number or vice-versa.

    Args:
        key: One of the representation code names or numbers specified in RP66 V1 Appendix B
        from_value: When True, converts number to code, when False, converts code to number

    Returns:
        Depending on from_value attribute, either a Representation Code or the corresponding number

    Raises:
        Exception: If key is not in representation_code_dictionary keys or values depending on the from_value attribute.

    .. _RP66 V1 Appendix B Representation Codes:
        http://w3.energistics.org/rp66/v1/rp66v1_appb.html

    """
    
    representation_code_dictionary = {
        'FSHORT': 1,
        'FSINGL': 2,
        'FSING1': 3,
        'FSING2': 4,
        'ISINGL': 5,
        'VSINGL': 6,
        'FDOUBL': 7,
        'FDOUB1': 8,
        'FDOUB2': 9,
        'CSINGL': 10,
        'CDOUBL': 11,
        'SSHORT': 12,
        'SNORM': 13,
        'SLONG': 14,
        'USHORT': 15,
        'UNORM': 16,
        'ULONG': 17,
        'UVARI': 18,
        'IDENT': 19,
        'ASCII': 20,
        'DTIME': 21,
        'ORIGIN': 22,
        'OBNAME': 23,
        'OBJREF': 24,
        'ATTREF': 25,
        'STATUS': 26,
        'UNITS': 27
    }

    if key not in list(representation_code_dictionary.keys()) and not from_value:

        error_message = f'Provided representation code "{key}" could not be found\nKey must be exactly one of the following:\n'
        error_message += ''.join(['\t' + key + '\n' for key in list(representation_code_dictionary.keys())])
        raise Exception(error_message)

    if key not in list(representation_code_dictionary.values()) and from_value:

        error_message = f'Provided description "{key}" could not be found\nKey must be exactly one of the following:\n'
        error_message += ''.join(['\t' + key + '\n' for key in list(representation_code_dictionary.values())])
        raise Exception(error_message)

    if from_value:
        return list(representation_code_dictionary.keys())[list(representation_code_dictionary.values()).index(key)]

    else:
        return representation_code_dictionary[key]