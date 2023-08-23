from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Equipment(EFLR):
    set_type = 'EQUIPMENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.trademark_name = None
        self.status = None
        self._type = None
        self.serial_number = None
        self.location = None
        self.height = None
        self.length = None
        self.minimum_diameter = None
        self.maximum_diameter = None
        self.volume = None
        self.weight = None
        self.hole_size = None
        self.pressure = None
        self.temperature = None
        self.vertical_depth = None
        self.radial_drift = None
        self.angular_drift = None

        self.create_attributes()
