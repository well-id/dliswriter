from dlis_writer.logical_record.core import EFLR


class Parameter(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'
        self.set_type = 'PARAMETER'

        self.long_name = None
        self.dimension = None
        self.axis = None
        self.zones = None
        self.values = None

        self.create_attributes()
