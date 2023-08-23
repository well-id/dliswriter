from dlis_writer.logical_record.core import EFLR


class Splice(EFLR):
    set_type = 'SPLICE'
    logical_record_type = 'STATIC'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.output_channels = None
        self.input_channels = None
        self.zones = None

        self.create_attributes()
