from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Parameter(EFLR):
    set_type = 'PARAMETER'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.long_name = self._create_attribute('long_name')
        self.dimension = self._create_attribute('dimension')
        self.axis = self._create_attribute('axis')
        self.zones = self._create_attribute('zones')
        self.values = self._create_attribute('values')
