from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, ListAttribute, DTimeAttribute


class Message(EFLR):
    set_type = 'MESSAGE'
    logical_record_type = LogicalRecordType.SCRIPT

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self._type = Attribute('_type', representation_code=RepC.IDENT)
        self.time = DTimeAttribute('time', allow_float=True)
        self.borehole_drift = Attribute('borehole_drift', converter=float)
        self.vertical_depth = Attribute('vertical_depth', converter=float)
        self.radial_drift = Attribute('radial_drift', converter=float)
        self.angular_drift = Attribute('angular_drift', converter=float)
        self.text = ListAttribute('text', representation_code=RepC.ASCII)

        self.set_attributes(**kwargs)


class Comment(EFLR):
    set_type = 'COMMENT'
    logical_record_type = LogicalRecordType.SCRIPT

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.text = ListAttribute('text', representation_code=RepC.ASCII)

        self.set_attributes(**kwargs)
