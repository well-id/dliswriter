from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


class LongName(EFLR):
    set_type = 'LONG-NAME'
    logical_record_type = LogicalRecordType.LNAME

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.general_modifier = self._create_attribute(
            'general_modifier', converter=self.convert_values, representation_code=RepC.ASCII, multivalued=True)
        self.quantity = self._create_attribute('quantity', representation_code=RepC.ASCII)
        self.quantity_modifier = self._create_attribute(
            'quantity_modifier', converter=self.convert_values, representation_code=RepC.ASCII, multivalued=True)
        self.altered_form = self._create_attribute('altered_form', representation_code=RepC.ASCII)
        self.entity = self._create_attribute('entity', representation_code=RepC.ASCII)
        self.entity_modifier = self._create_attribute(
            'entity_modifier', converter=self.convert_values, representation_code=RepC.ASCII, multivalued=True)
        self.entity_number = self._create_attribute('entity_number', representation_code=RepC.ASCII)
        self.entity_part = self._create_attribute('entity_part', representation_code=RepC.ASCII)
        self.entity_part_number = self._create_attribute('entity_part_number', representation_code=RepC.ASCII)
        self.generic_source = self._create_attribute('generic_source', representation_code=RepC.ASCII)
        self.source_part = self._create_attribute(
            'source_part', converter=self.convert_values, multivalued=True, representation_code=RepC.ASCII)
        self.source_part_number = self._create_attribute(
            'source_part_number', converter=self.convert_values, multivalued=True, representation_code=RepC.ASCII)
        self.conditions = self._create_attribute(
            'conditions', converter=self.convert_values, multivalued=True, representation_code=RepC.ASCII)
        self.standard_symbol = self._create_attribute('standard_symbol', representation_code=RepC.ASCII)
        self.private_symbol = self._create_attribute('private_symbol', representation_code=RepC.ASCII)

        self.set_attributes(**kwargs)
