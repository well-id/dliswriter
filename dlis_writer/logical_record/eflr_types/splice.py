from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Splice(EFLR):
    set_type = 'SPLICE'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.output_channels = None
        self.input_channels = None
        self.zones = None

        self.create_attributes()
