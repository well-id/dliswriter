from .utils.core import EFLR


class Axis(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'AXIS'
        self.set_type = 'AXIS'

        self.axis_id = None
        self.coordinates = None
        self.spacing = None

        self.create_attributes()