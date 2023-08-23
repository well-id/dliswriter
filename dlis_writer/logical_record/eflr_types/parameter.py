from dlis_writer.logical_record.core import EFLR


class Parameter(EFLR):
    set_type = 'PARAMETER'
    logical_record_type = 'STATIC'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.long_name = None
        self.dimension = None
        self.axis = None
        self.zones = None
        self.values = None

        self.create_attributes()
