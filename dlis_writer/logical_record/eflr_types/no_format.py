from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


class NoFormatObject(EFLRObject):

    def __init__(self, name: str, parent: "NoFormat", **kwargs):

        self.consumer_name = Attribute('consumer_name', representation_code=RepC.IDENT)
        self.description = Attribute('description', representation_code=RepC.ASCII)

        super().__init__(name, parent, **kwargs)


class NoFormat(EFLR):
    set_type = 'NO-FORMAT'
    logical_record_type = EFLRType.UDI
    object_type = NoFormatObject
