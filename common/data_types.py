from struct import Struct

from converters import get_datetime

# FSHORT = Struct('>h')
# def read_fshort(value):
# 	''' 2 bytes Low precision floating point '''
# 	return FSHORT.unpack(value)
# def write_fshort(value):
# 	return FSHORT.pack(value)



# UNORM = Struct('>H')
# USHORT = Struct('>B')


# def read_unorm(value):
# 	''' 2 bytes unsigned integer '''
# 	return UNORM.pack(value)

# def read_ushort(value):
# 	''' 1 byte unsigned integer '''
# 	return USHORT.pack(value)


struct_type_dict = {
	'FSHORT': Struct('>h'),
	'FSINGL': Struct('>f'),
	'FSING1': Struct('>ff'),
	'FSING2': Struct('>fff'),
	'ISINGL': Struct('>i'),
	'VSINGL': Struct('>i'),
	'FDOUBL': Struct('>d'),
	'FDOUB1': Struct('>dd'),
	'FDOUB2': Struct('>ddd'),
	'CSINGL': Struct('>ff'),
	'CDOUBL': Struct('>dd'),
	'SSHORT': Struct('>b'),
	'SNORM': Struct('>h'),
	'SLONG': Struct('>i'),
	'USHORT': Struct('>B'),
	'UNORM': Struct('>H'),
	'ULONG': Struct('>I'),
	'UVARI': None,
	'IDENT': None,
	'ASCII': None,
	'DTIME': Struct('>BBBBBBH'),
	'ORIGIN': None,
	'OBNAME': None,
	'OBJREF': None,
	'ATTREF': None,
	'STATUS': Struct('>B'),
	'UNITS': None

}

def read_struct(struct_type, packed_value):
	return struct_type_dict[struct_type].unpack(packed_value)[0]

def write_struct(struct_type, value):
	if struct_type == 'ASCII':
		return value.encode('ascii')
	elif struct_type == 'UVARI':
	    if value > 127:
	    	if value > 16383:
	    		value = '{0:08b}'.format(value)
	    		value = '11' + (30 - len(value)) * '0' + value
	    		return write_struct('ULONG', int(value,2))
	    	else:
	    		value = '{0:08b}'.format(value)
	    		value = '10' + (14 - len(value)) * '0' + value
	    		return write_struct('UNORM', int(value,2))
	    		
	    return write_struct('USHORT',int('{0:08b}'.format(value),2))

	elif struct_type == 'IDENT':
		return write_struct('USHORT', len(value)) + value.encode('ascii')

	elif struct_type == 'DTIME':
		return get_datetime(value)
	else:
		return struct_type_dict[struct_type].pack(value)


