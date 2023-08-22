from dlis_writer.logical_record.core import EFLR


class Splice(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'
        self.set_type = 'SPLICE'

        self.output_channels = None
        self.input_channels = None
        self.zones = None

        self.create_attributes()