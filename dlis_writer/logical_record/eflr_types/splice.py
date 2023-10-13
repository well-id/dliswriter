from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Splice(EFLR):
    set_type = 'SPLICE'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.output_channels = self._create_attribute('output_channels')
        self.input_channels = self._create_attribute('input_channels')
        self.zones = self._create_attribute('zones')

        self.set_attributes(**kwargs)
