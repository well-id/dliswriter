from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Axis(EFLR):
    set_type = 'AXIS'
    logical_record_type = LogicalRecordType.AXIS
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.axis_id = self._create_attribute('axis_id')
        self.coordinates = self._create_attribute('coordinates')
        self.spacing = self._create_attribute('spacing')
