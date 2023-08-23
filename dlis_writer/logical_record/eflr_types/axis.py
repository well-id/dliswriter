from dlis_writer.logical_record.core import EFLR


class Axis(EFLR):
    set_type = 'AXIS'
    logical_record_type = 'AXIS'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.axis_id = None
        self.coordinates = None
        self.spacing = None

        self.create_attributes()
