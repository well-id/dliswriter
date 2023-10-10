from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Tool(EFLR):
    set_type = 'TOOL'
    logical_record_type = LogicalRecordType.STATIC
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.description = self._create_attribute('description')
        self.trademark_name = self._create_attribute('trademark_name')
        self.generic_name = self._create_attribute('generic_name')
        self.parts = self._create_attribute('parts')
        self.status = self._create_attribute('status')
        self.channels = self._create_attribute('channels')
        self.parameters = self._create_attribute('parameters')

        self.set_attributes(**kwargs)