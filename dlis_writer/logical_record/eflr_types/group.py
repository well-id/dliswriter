from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Group(EFLR):
    set_type = 'GROUP'
    logical_record_type = LogicalRecordType.STATIC
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.description = self._create_attribute('description')
        self.object_type = self._create_attribute('object_type')
        self.object_list = self._create_attribute('object_list')
        self.group_list = self._create_attribute('group_list')

        self.set_attributes(**kwargs)
