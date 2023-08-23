from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Axis(EFLR):
    set_type = 'AXIS'
    logical_record_type = LogicalRecordType.AXIS

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.axis_id = None
        self.coordinates = None
        self.spacing = None

        self.create_attributes()
