from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Frame(EFLR):
    set_type = 'FRAME'
    logical_record_type = LogicalRecordType.FRAME

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.description = None
        self.channels = None
        self.index_type = None
        self.direction = None
        self.spacing = None
        self.encrypted = None
        self.index_min = None
        self.index_max = None

        self.create_attributes()