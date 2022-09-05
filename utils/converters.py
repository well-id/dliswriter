import struct


def get_ascii_bytes(value, required_length, justify=None):
    '''
    :value = Value to convert to ascii bytes
    :required_length = Specified ascii string length
    :justify = When the length of the value is less than required length,
    trailing or preciding blanks/zeros is required depending on the data type.
    The default value is None which equals to justifying the value to the right and
    and filling the remaining required characters with PRECIDING "blanks".
    justify="left" adds TRAILING blanks
    '''

    if justify == 'left':
        return (str(value) + (required_length - len(str(value))) * ' ').encode('ascii')
    return ((required_length - len(str(value))) * ' ' + str(value)).encode('ascii')


def get_logical_record_type(description:str):
    '''

    There are 11 Logical Record CODES specified in: http://w3.energistics.org/rp66/v1/rp66v1_appa.html
    This method basically takes description of the Logical Record Type and returns the corresponding code.

    '''

    logical_record_type_dictionary = {
        'FILE-HEADER': 0,
        'ORIGIN': 1,
        'AXIS': 2,
        'CHANNEL': 3,
        'FRAME': 4,
        'STATIC': 5,
        'SCRIPT': 6,
        'UPDATE': 7,
        'UNFORMATTED-DATA-IDENTIFIER': 8,
        'LONG-NAME': 9,
        'SPECIFICATION': 10,
        'DICTIONARY': 11
    }


    if description not in list(logical_record_type_dictionary.keys()):

        error_message = f'Provided description "{description}" could not be found\nDescription must be exactly one of the following:\n'
        error_message += ''.join(['\t' + description + '\n' for description in list(logical_record_type_dictionary.keys())])
        raise Exception(error_message)

    return logical_record_type_dictionary[description]

def get_representation_code(description:str):
    '''

    There are 27 representation codes defined in RP66 V1 Appendix B -> http://w3.energistics.org/rp66/v1/rp66v1_appb.html

    :description must be one of the following
        FSHORT
        FSINGL
        FSING1
        FSING2
        ISINGL
        VSINGL
        FDOUBL
        FDOUB1
        FDOUB2
        CSINGL
        CDOUBL
        SSHORT
        SNORM
        SLONG
        USHORT
        UNORM
        ULONG
        UVARI
        IDENT
        ASCII
        DTIME
        ORIGIN
        OBNAME
        OBJREF
        ATTREF
        STATUS
        UNITS

    :returns the corresponding code

    '''
    
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

    if description not in list(representation_code_dictionary.keys()):

        error_message = f'Provided description "{description}" could not be found\nDescription must be exactly one of the following:\n'
        error_message += ''.join(['\t' + description + '\n' for description in list(representation_code_dictionary.keys())])
        raise Exception(error_message)

    return representation_code_dictionary[description]


