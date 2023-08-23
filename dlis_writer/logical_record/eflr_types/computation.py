from dlis_writer.logical_record.core import EFLR


class Computation(EFLR):
    set_type = 'COMPUTATION'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'

        self.long_name = None
        self.properties = None
        self.dimension = None
        self.axis = None
        self.zones = None
        self.values = None
        self.source = None

        self.create_attributes()
