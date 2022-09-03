from struct import Struct
import re

from utils.converters import get_datetime



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

def validate_units(value:str):
	'''

	:value -> A string representing the units.

	:returns -> Validates the "value" and returns after converting to bytes
	as per RP66 V1 specifications.

	
	Validates the user input for UNITS data type according to
	RP66 V1 specifications.

	QUOTE
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

	END QUOTE FROM -> RP66 V1 Appendix B.27 -> http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_27

	References:

		-> http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_27
	'''
	
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


def read_struct(struct_type, packed_value):
	return struct_type_dict[struct_type].unpack(packed_value)[0]

def write_struct(struct_type, value):
	

	if struct_type == 'ASCII':
		return write_struct('UVARI', len(str(value))) + str(value).encode('ascii')
	

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
		return write_struct('USHORT', len(str(value))) + str(value).encode('ascii')

	
	elif struct_type == 'DTIME':
		return get_datetime(value)

	elif struct_type == 'OBNAME':
		''' value must be passed as a tuple (origin, copy_number, name) '''
		origin_reference = write_struct('UVARI', value[0])
		copy_number = write_struct('USHORT', value[1])
		name = write_struct('IDENT', value[2])

		return origin_reference + copy_number + name

	elif struct_type == 'UNITS':
		return write_struct('IDENT', validate_units(value))



	else:
		return struct_type_dict[struct_type].pack(value)


