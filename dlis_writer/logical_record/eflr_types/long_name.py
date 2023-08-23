from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class LongName(EFLR):
    set_type = 'LONG-NAME'
    logical_record_type = LogicalRecordType.LNAME

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.general_modifier = None
        self.quantity = None
        self.quantity_modifier = None
        self.altered_form = None
        self.entity = None
        self.entity_modifier = None
        self.entity_number = None
        self.entity_part = None
        self.entity_part_number = None
        self.generic_source = None
        self.source_part = None
        self.source_part_number = None
        self.conditions = None
        self.standard_symbol = None
        self.private_symbol = None

        self.create_attributes()

