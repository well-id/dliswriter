from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Message(EFLR):
    set_type = 'MESSAGE'
    logical_record_type = LogicalRecordType.SCRIPT

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._type = None
        self.time = None
        self.borehole_drift = None
        self.vertical_depth = None
        self.radial_drift = None
        self.angular_drift = None
        self.text = None

        self.create_attributes()


class Comment(EFLR):
    set_type = 'COMMENT'
    logical_record_type = LogicalRecordType.SCRIPT

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.text = None

        self.create_attributes()
