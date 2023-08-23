from dlis_writer.logical_record.core import EFLR


class Group(EFLR):
    set_type = 'GROUP'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'

        self.description = None
        self.object_type = None
        self.object_list = None
        self.group_list = None

        self.create_attributes()
