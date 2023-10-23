from dlis_writer.logical_record.core.eflr import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, ListAttribute


class Axis(EFLR):
    set_type = 'AXIS'
    logical_record_type = LogicalRecordType.AXIS

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.axis_id = Attribute('axis_id', representation_code=RepC.IDENT)
        self.coordinates = ListAttribute('coordinates', converter=Attribute.convert_numeric)
        self.spacing = Attribute('spacing', converter=float)

        self.set_attributes(**kwargs)
