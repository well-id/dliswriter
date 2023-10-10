from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class LongName(EFLR):
    set_type = 'LONG-NAME'
    logical_record_type = LogicalRecordType.LNAME
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.general_modifier = self._create_attribute('general_modifier')
        self.quantity = self._create_attribute('quantity')
        self.quantity_modifier = self._create_attribute('quantity_modifier')
        self.altered_form = self._create_attribute('altered_form')
        self.entity = self._create_attribute('entity')
        self.entity_modifier = self._create_attribute('entity_modifier')
        self.entity_number = self._create_attribute('entity_number')
        self.entity_part = self._create_attribute('entity_part')
        self.entity_part_number = self._create_attribute('entity_part_number')
        self.generic_source = self._create_attribute('generic_source')
        self.source_part = self._create_attribute('source_part')
        self.source_part_number = self._create_attribute('source_part_number')
        self.conditions = self._create_attribute('conditions')
        self.standard_symbol = self._create_attribute('standard_symbol')
        self.private_symbol = self._create_attribute('private_symbol')

        self.set_attributes(**kwargs)
