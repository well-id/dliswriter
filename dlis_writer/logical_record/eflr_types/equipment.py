from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


class Equipment(EFLR):
    set_type = 'EQUIPMENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.trademark_name = self._create_attribute('trademark_name', representation_code=RepC.ASCII)
        self.status = self._create_attribute('status', converter=int, representation_code=RepC.STATUS)
        self._type = self._create_attribute('_type', representation_code=RepC.IDENT)
        self.serial_number = self._create_attribute('serial_number', representation_code=RepC.IDENT)
        self.location = self._create_attribute('location', representation_code=RepC.IDENT)
        self.height = self._create_attribute('height', converter=float, representation_code=RepC.FDOUBL)
        self.length = self._create_attribute('length', converter=float, representation_code=RepC.FDOUBL)
        self.minimum_diameter = self._create_attribute(
            'minimum_diameter', converter=float, representation_code=RepC.FDOUBL)
        self.maximum_diameter = self._create_attribute(
            'maximum_diameter', converter=float, representation_code=RepC.FDOUBL)
        self.volume = self._create_attribute('volume', converter=float, representation_code=RepC.FDOUBL)
        self.weight = self._create_attribute('weight', converter=float, representation_code=RepC.FDOUBL)
        self.hole_size = self._create_attribute('hole_size', converter=float, representation_code=RepC.FDOUBL)
        self.pressure = self._create_attribute('pressure', converter=float, representation_code=RepC.FDOUBL)
        self.temperature = self._create_attribute('temperature', converter=float, representation_code=RepC.FDOUBL)
        self.vertical_depth = self._create_attribute(
            'vertical_depth', converter=float, representation_code=RepC.FDOUBL)
        self.radial_drift = self._create_attribute(
            'radial_drift', converter=float, representation_code=RepC.FDOUBL)
        self.angular_drift = self._create_attribute(
            'angular_drift', converter=float, representation_code=RepC.FDOUBL)

        self.set_attributes(**kwargs)
