from .utils.core import EFLR


class Channel(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'CHANNL'
        self.set_type = 'CHANNEL'

        self.long_name = None
        self.properties = None
        self.representation_code = None
        self.units = None
        self.dimension = None
        self.axis = None
        self.element_limit = None
        self.source = None
        self.minimum_value = None
        self.maximum_value = None

        self.create_attributes()
        self.data = None
