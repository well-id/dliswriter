from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Tool(EFLR):
    set_type = 'TOOL'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.description = None
        self.trademark_name = None
        self.generic_name = None
        self.parts = None
        self.status = None
        self.channels = None
        self.parameters = None

        self.create_attributes()
