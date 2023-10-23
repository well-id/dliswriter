from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


class WellReferencePoint(EFLR):
    set_type = 'WELL-REFERENCE'
    logical_record_type = LogicalRecordType.OLR

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.permanent_datum = self._create_attribute('permanent_datum', representation_code=RepC.ASCII)
        self.vertical_zero = self._create_attribute('vertical_zero', representation_code=RepC.ASCII)
        self.permanent_datum_elevation = self._create_attribute(
            'permanent_datum_elevation', converter=float, representation_code=RepC.FDOUBL)
        self.above_permanent_datum = self._create_attribute(
            'above_permanent_datum', converter=float, representation_code=RepC.FDOUBL)
        self.magnetic_declination = self._create_attribute(
            'magnetic_declination', converter=float, representation_code=RepC.FDOUBL)
        self.coordinate_1_name = self._create_attribute('coordinate_1_name', representation_code=RepC.ASCII)
        self.coordinate_1_value = self._create_attribute(
            'coordinate_1_value', converter=float, representation_code=RepC.FDOUBL)
        self.coordinate_2_name = self._create_attribute('coordinate_2_name', representation_code=RepC.ASCII)
        self.coordinate_2_value = self._create_attribute(
            'coordinate_2_value', converter=float, representation_code=RepC.FDOUBL)
        self.coordinate_3_name = self._create_attribute('coordinate_3_name', representation_code=RepC.ASCII)
        self.coordinate_3_value = self._create_attribute(
            'coordinate_3_value', converter=float, representation_code=RepC.FDOUBL)

        self.set_attributes(**kwargs)
