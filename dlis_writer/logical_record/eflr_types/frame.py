from dlis_writer.logical_record.core import EFLR


class Frame(EFLR):
    set_type = 'FRAME'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'FRAME'

        self.description = None
        self.channels = None
        self.index_type = None
        self.direction = None
        self.spacing = None
        self.encrypted = None
        self.index_min = None
        self.index_max = None

        self.create_attributes()
