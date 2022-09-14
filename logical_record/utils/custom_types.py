from typing import Literal
from typing import Union
from typing import List
from typing import Tuple

RepresentationCode = Literal['FSHORT', 'FSINGL', 'FSING1', 'FSING2', 'ISINGL', 'VSINGL', 'FDOUBL',
							 'FDOUB1', 'FDOUB2', 'CSINGL', 'CDOUBL', 'SSHORT', 'SNORM', 'SLONG',
							 'USHORT', 'UNORM', 'ULONG', 'UVARI', 'IDENT', 'ASCII', 'DTIME',
							 'ORIGIN', 'OBNAME', 'OBJREF', 'ATTREF', 'STATUS', 'UNITS']

RepresentationCodeNumber = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
								   11, 12, 13, 14, 15, 16, 17, 18,
								   19, 20, 21, 22, 23, 24, 25, 26, 27]

Justify = Literal['left', 'right', None]

LogicalRecordType = Literal['FHLR', 'OLR', 'AXIS', 'CHANNL', 'FRAME', 'STATIC', 'SCRIPT',
							'UPDATE', 'UDI', 'LNAME', 'SPEC', 'DICT']

LogicalRecordTypeCode = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

AttributeValue = Union[int, float, str, List[int], List[float], List[str], Tuple[int], Tuple[float], Tuple[str]]