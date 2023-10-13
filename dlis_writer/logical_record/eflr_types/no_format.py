from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class NoFormat(EFLR):
    set_type = 'NO-FORMAT'
    logical_record_type = LogicalRecordType.UDI

    def __init__(self, object_name: str, set_name: str = None, **kwargs):

        super().__init__(object_name, set_name)

        self.consumer_name = self._create_attribute('consumer_name')
        self.description = self._create_attribute('description')

        self.set_attributes(**kwargs)
