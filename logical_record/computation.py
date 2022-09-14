from .utils.core import EFLR


class Computation(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'
        self.set_type = 'COMPUTATION'
        
        self.long_name = None
        self.properties = None
        self.dimension = None
        self.axis = None
        self.zones = None
        self.values = None
        self.source = None

        self.create_attributes()