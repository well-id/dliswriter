from dlis_writer.logical_record.core import EFLR


class Origin(EFLR):
    
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'OLR'
        self.set_type = 'ORIGIN'

        self.file_id = None
        self.file_set_name = None
        self.file_set_number = None
        self.file_number = None
        self.file_type = None
        self.product = None
        self.version = None
        self.programs = None
        self.creation_time = None
        self.order_number = None
        self.descent_number = None
        self.run_number = None
        self.well_id = None
        self.well_name = None
        self.field_name = None
        self.producer_code = None
        self.producer_name = None
        self.company = None
        self.name_space_name = None
        self.name_space_version = None

        self.create_attributes()

    @property
    def key(self):
        return hash(type(self))
