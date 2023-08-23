from dlis_writer.logical_record.core import EFLR


class Group(EFLR):
    set_type = 'GROUP'
    logical_record_type = 'STATIC'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.description = None
        self.object_type = None
        self.object_list = None
        self.group_list = None

        self.create_attributes()
