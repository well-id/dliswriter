from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class NoFormat(EFLR):
    set_type = 'NO-FORMAT'
    logical_record_type = LogicalRecordType.UDI

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.consumer_name = None
        self.description = None

        self.create_attributes()