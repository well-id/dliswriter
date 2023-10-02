from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Message(EFLR):
    set_type = 'MESSAGE'
    logical_record_type = LogicalRecordType.SCRIPT
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._type = self._create_attribute('_type')
        self.time = self._create_attribute('time')
        self.borehole_drift = self._create_attribute('borehole_drift')
        self.vertical_depth = self._create_attribute('vertical_depth')
        self.radial_drift = self._create_attribute('radial_drift')
        self.angular_drift = self._create_attribute('angular_drift')
        self.text = self._create_attribute('text')


class Comment(EFLR):
    set_type = 'COMMENT'
    logical_record_type = LogicalRecordType.SCRIPT
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.text = self._create_attribute('text')
