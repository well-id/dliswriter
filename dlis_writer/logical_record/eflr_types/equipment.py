from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Equipment(EFLR):
    set_type = 'EQUIPMENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.trademark_name = self._create_attribute('trademark_name')
        self.status = self._create_attribute('status', converter=int)
        self._type = self._create_attribute('_type')
        self.serial_number = self._create_attribute('serial_number')
        self.location = self._create_attribute('location')
        self.height = self._create_attribute('height', converter=float)
        self.length = self._create_attribute('length', converter=float)
        self.minimum_diameter = self._create_attribute('minimum_diameter', converter=float)
        self.maximum_diameter = self._create_attribute('maximum_diameter', converter=float)
        self.volume = self._create_attribute('volume', converter=float)
        self.weight = self._create_attribute('weight', converter=float)
        self.hole_size = self._create_attribute('hole_size', converter=float)
        self.pressure = self._create_attribute('pressure', converter=float)
        self.temperature = self._create_attribute('temperature', converter=float)
        self.vertical_depth = self._create_attribute('vertical_depth', converter=float)
        self.radial_drift = self._create_attribute('radial_drift', converter=float)
        self.angular_drift = self._create_attribute('angular_drift', converter=float)

        self.set_attributes(**kwargs)
