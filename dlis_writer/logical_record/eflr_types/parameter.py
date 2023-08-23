from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Parameter(EFLR):
    set_type = 'PARAMETER'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.long_name = None
        self.dimension = None
        self.axis = None
        self.zones = None
        self.values = None

        self.create_attributes()
