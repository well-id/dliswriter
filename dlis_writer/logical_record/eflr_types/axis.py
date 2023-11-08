from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute


class AxisObject(EFLRObject):

    def __init__(self, name: str, parent, **kwargs):

        self.axis_id = Attribute('axis_id', representation_code=RepC.IDENT)
        self.coordinates = NumericAttribute('coordinates', multivalued=True)
        self.spacing = NumericAttribute('spacing')

        super().__init__(name, parent, **kwargs)


class Axis(EFLR):
    set_type = 'AXIS'
    logical_record_type = EFLRType.AXIS
    object_type = AxisObject

