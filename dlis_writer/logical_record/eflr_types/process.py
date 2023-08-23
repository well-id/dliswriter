from dlis_writer.logical_record.core import EFLR


class Process(EFLR):
    set_type = 'PROCESS'
    logical_record_type = 'STATIC'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

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
