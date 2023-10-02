from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class NoFormat(EFLR):
    set_type = 'NO-FORMAT'
    logical_record_type = LogicalRecordType.UDI
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.consumer_name = self._create_attribute('consumer_name')
        self.description = self._create_attribute('description')
