from dlis_writer.logical_record.core.eflr import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Axis(EFLR):
    set_type = 'AXIS'
    logical_record_type = LogicalRecordType.AXIS

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.axis_id = self._create_attribute('axis_id')
        self.coordinates = self._create_attribute(
            'coordinates', converter=lambda val: self.convert_values(val, require_numeric=True))
        self.spacing = self._create_attribute('spacing', converter=float)

        self.set_attributes(**kwargs)
