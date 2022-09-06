import re
from struct import Struct

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


def get_datetime(date_time):

    '''

    RP66 V1 uses a specific datetime format.

    QUOTE


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
    END QUOTE FROM -> http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_21

    

    :date_time -> is a datetime.datetime object.

    :returns -> converted datetime in bytes

    Usage:
        from datetime import datetime

        now = datetime.now()
        converted_datetime = get_datetime(now)

    '''
    
    value = b''

    time_zone = '{0:04b}'.format(0) # Local Standard Time is set as default
    month = '{0:04b}'.format(date_time.month)


    value += write_struct('USHORT', date_time.year - 1900)
    value += write_struct('USHORT', int(time_zone + month, 2))
    value += write_struct('USHORT', date_time.day)
    value += write_struct('USHORT', date_time.hour)
    value += write_struct('USHORT', date_time.minute)
    value += write_struct('USHORT', date_time.second)
    value += write_struct('UNORM', int(date_time.microsecond / 1000))
    
    return value


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

	elif struct_type == 'OBJREF':
		return write_struct('IDENT', value.set_type) + value.get_obname_only()

	else:
		return struct_type_dict[struct_type].pack(value)


