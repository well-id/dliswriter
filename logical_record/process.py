from .utils.core import EFLR


class Process(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'
        self.set_type = 'PROCESS'

        self.description = None
        self.trademark_name = None
        self.version = None
        self.properties = None
        self.status = None
        self.input_channels = None
        self.output_channels = None
        self.input_computations = None
        self.output_computations = None
        self.parameters = None
        self.comments = None

        self.create_attributes()