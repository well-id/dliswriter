from typing import Literal
from typing import Union
from typing import List
from typing import Tuple


LogicalRecordType = Literal['FHLR', 'OLR', 'AXIS', 'CHANNL', 'FRAME', 'STATIC', 'SCRIPT',
							'UPDATE', 'UDI', 'LNAME', 'SPEC', 'DICT']

LogicalRecordTypeCode = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

AttributeValue = Union[int, float, str, List[int], List[float], List[str], Tuple[int], Tuple[float], Tuple[str]]