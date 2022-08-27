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