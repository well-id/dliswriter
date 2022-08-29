from common.data_types import struct_type_dict
from common.data_types import read_struct
from common.data_types import write_struct


print(write_struct('FSHORT', 2))
print(write_struct('FDOUB2', 2.3))
print(read_struct('FDOUB2', write_struct('FDOUB2', 2.3)))