from .utils.core import EFLR


class Tool(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'
        self.set_type = 'TOOL'

        self.description = None
        self.trademark_name = None
        self.generic_name = None
        self.parts = None
        self.status = None
        self.channels = None
        self.parameters = None

        self.create_attributes()