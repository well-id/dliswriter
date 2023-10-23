from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


class Equipment(EFLR):
    set_type = 'EQUIPMENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII)
        self.status = Attribute('status', converter=int, representation_code=RepC.STATUS)
        self._type = Attribute('_type', representation_code=RepC.IDENT)
        self.serial_number = Attribute('serial_number', representation_code=RepC.IDENT)
        self.location = Attribute('location', representation_code=RepC.IDENT)
        self.height = Attribute('height', converter=float, representation_code=RepC.FDOUBL)
        self.length = Attribute('length', converter=float, representation_code=RepC.FDOUBL)
        self.minimum_diameter = Attribute('minimum_diameter', converter=float, representation_code=RepC.FDOUBL)
        self.maximum_diameter = Attribute('maximum_diameter', converter=float, representation_code=RepC.FDOUBL)
        self.volume = Attribute('volume', converter=float, representation_code=RepC.FDOUBL)
        self.weight = Attribute('weight', converter=float, representation_code=RepC.FDOUBL)
        self.hole_size = Attribute('hole_size', converter=float, representation_code=RepC.FDOUBL)
        self.pressure = Attribute('pressure', converter=float, representation_code=RepC.FDOUBL)
        self.temperature = Attribute('temperature', converter=float, representation_code=RepC.FDOUBL)
        self.vertical_depth = Attribute('vertical_depth', converter=float, representation_code=RepC.FDOUBL)
        self.radial_drift = Attribute('radial_drift', converter=float, representation_code=RepC.FDOUBL)
        self.angular_drift = Attribute('angular_drift', converter=float, representation_code=RepC.FDOUBL)

        self.set_attributes(**kwargs)
