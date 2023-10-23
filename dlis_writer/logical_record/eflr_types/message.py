from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Message(EFLR):
    set_type = 'MESSAGE'
    logical_record_type = LogicalRecordType.SCRIPT

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self._type = self._create_attribute('_type')
        self.time = self._create_attribute('time', converter=self.parse_dtime)
        self.borehole_drift = self._create_attribute('borehole_drift', converter=float)
        self.vertical_depth = self._create_attribute('vertical_depth', converter=float)
        self.radial_drift = self._create_attribute('radial_drift', converter=float)
        self.angular_drift = self._create_attribute('angular_drift', converter=float)
        self.text = self._create_attribute('text', converter=self.convert_values)

        self.set_attributes(**kwargs)


class Comment(EFLR):
    set_type = 'COMMENT'
    logical_record_type = LogicalRecordType.SCRIPT

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.text = self._create_attribute('text', converter=self.convert_values)

        self.set_attributes(**kwargs)
