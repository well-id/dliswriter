from .utils.core import EFLR
from .utils.common import write_struct

class NoFormat(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'UDI'
        self.set_type = 'NO-FORMAT'

        self.consumer_name = None
        self.description = None

        self.create_attributes()