from .utils.core import EFLR


class LongName(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'LNAME'
        self.set_type = 'LONG-NAME'

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

