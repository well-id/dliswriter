from dlis_writer.logical_record.core import EFLR


class Message(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'SCRIPT'
        self.set_type = 'MESSAGE'

        self._type = None
        self.time = None
        self.borehole_drift = None
        self.vertical_depth = None
        self.radial_drift = None
        self.angular_drift = None
        self.text = None

        self.create_attributes()


class Comment(EFLR):
    
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'SCRIPT'
        self.set_type = 'COMMENT'

        self.text = None

        self.create_attributes()