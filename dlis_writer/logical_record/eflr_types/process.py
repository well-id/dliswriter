from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Process(EFLR):
    set_type = 'PROCESS'
    logical_record_type = LogicalRecordType.STATIC
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, object_name: str, set_name: str = None, **kwargs):

        super().__init__(object_name, set_name)

        self.description = self._create_attribute('description')
        self.trademark_name = self._create_attribute('trademark_name')
        self.version = self._create_attribute('version')
        self.properties = self._create_attribute('properties')
        self.status = self._create_attribute('status')
        self.input_channels = self._create_attribute('input_channels')
        self.output_channels = self._create_attribute('output_channels')
        self.input_computations = self._create_attribute('input_computations')
        self.output_computations = self._create_attribute('output_computations')
        self.parameters = self._create_attribute('parameters')
        self.comments = self._create_attribute('comments')

        self.set_attributes(**kwargs)
