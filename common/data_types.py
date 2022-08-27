from struct import Struct

UNORM = Struct('>H')
USHORT = Struct('>B')


def get_unorm(value):
	''' 2 bytes unsigned integer '''
	return UNORM.pack(value)

def get_ushort(value):
	''' 1 byte unsigned integer '''
	return USHORT.pack(value)