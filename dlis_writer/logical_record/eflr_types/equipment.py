from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Equipment(EFLR):
    set_type = 'EQUIPMENT'
    logical_record_type = LogicalRecordType.STATIC
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.trademark_name = self._create_attribute('trademark_name')
        self.status = self._create_attribute('status')
        self._type = self._create_attribute('_type')
        self.serial_number = self._create_attribute('serial_number')
        self.location = self._create_attribute('location')
        self.height = self._create_attribute('height')
        self.length = self._create_attribute('length')
        self.minimum_diameter = self._create_attribute('minimum_diameter')
        self.maximum_diameter = self._create_attribute('maximum_diameter')
        self.volume = self._create_attribute('volume')
        self.weight = self._create_attribute('weight')
        self.hole_size = self._create_attribute('hole_size')
        self.pressure = self._create_attribute('pressure')
        self.temperature = self._create_attribute('temperature')
        self.vertical_depth = self._create_attribute('vertical_depth')
        self.radial_drift = self._create_attribute('radial_drift')
        self.angular_drift = self._create_attribute('angular_drift')
