from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


class WellReferencePoint(EFLR):
    set_type = 'WELL-REFERENCE'
    logical_record_type = LogicalRecordType.OLR

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.permanent_datum = Attribute('permanent_datum', representation_code=RepC.ASCII)
        self.vertical_zero = Attribute('vertical_zero', representation_code=RepC.ASCII)
        self.permanent_datum_elevation = Attribute(
            'permanent_datum_elevation', converter=float, representation_code=RepC.FDOUBL)
        self.above_permanent_datum = Attribute(
            'above_permanent_datum', converter=float, representation_code=RepC.FDOUBL)
        self.magnetic_declination = Attribute(
            'magnetic_declination', converter=float, representation_code=RepC.FDOUBL)
        self.coordinate_1_name = Attribute('coordinate_1_name', representation_code=RepC.ASCII)
        self.coordinate_1_value = Attribute(
            'coordinate_1_value', converter=float, representation_code=RepC.FDOUBL)
        self.coordinate_2_name = Attribute('coordinate_2_name', representation_code=RepC.ASCII)
        self.coordinate_2_value = Attribute(
            'coordinate_2_value', converter=float, representation_code=RepC.FDOUBL)
        self.coordinate_3_name = Attribute('coordinate_3_name', representation_code=RepC.ASCII)
        self.coordinate_3_value = Attribute(
            'coordinate_3_value', converter=float, representation_code=RepC.FDOUBL)

        self.set_attributes(**kwargs)
