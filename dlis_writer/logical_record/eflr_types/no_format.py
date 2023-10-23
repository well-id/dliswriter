from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


class NoFormat(EFLR):
    set_type = 'NO-FORMAT'
    logical_record_type = LogicalRecordType.UDI

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.consumer_name = self._create_attribute('consumer_name', representation_code=RepC.IDENT)
        self.description = self._create_attribute('description', representation_code=RepC.ASCII)

        self.set_attributes(**kwargs)
