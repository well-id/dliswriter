from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute


class Equipment(EFLR):
    set_type = 'EQUIPMENT'
    logical_record_type = EFLRType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII)
        self.status = Attribute('status', converter=int, representation_code=RepC.STATUS)
        self._type = Attribute('_type', representation_code=RepC.IDENT)
        self.serial_number = Attribute('serial_number', representation_code=RepC.IDENT)
        self.location = Attribute('location', representation_code=RepC.IDENT)
        self.height = NumericAttribute('height')
        self.length = NumericAttribute('length')
        self.minimum_diameter = NumericAttribute('minimum_diameter')
        self.maximum_diameter = NumericAttribute('maximum_diameter')
        self.volume = NumericAttribute('volume')
        self.weight = NumericAttribute('weight')
        self.hole_size = NumericAttribute('hole_size')
        self.pressure = NumericAttribute('pressure')
        self.temperature = NumericAttribute('temperature')
        self.vertical_depth = NumericAttribute('vertical_depth')
        self.radial_drift = NumericAttribute('radial_drift')
        self.angular_drift = NumericAttribute('angular_drift')

        self.set_attributes(**kwargs)
