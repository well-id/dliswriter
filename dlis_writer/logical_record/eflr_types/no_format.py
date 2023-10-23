from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


class NoFormat(EFLR):
    set_type = 'NO-FORMAT'
    logical_record_type = LogicalRecordType.UDI

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.consumer_name = Attribute('consumer_name', representation_code=RepC.IDENT)
        self.description = Attribute('description', representation_code=RepC.ASCII)

        self.set_attributes(**kwargs)
