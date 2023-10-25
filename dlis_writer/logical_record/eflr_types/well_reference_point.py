from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute


class WellReferencePoint(EFLR):
    set_type = 'WELL-REFERENCE'
    logical_record_type = LogicalRecordType.OLR

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.permanent_datum = Attribute('permanent_datum', representation_code=RepC.ASCII)
        self.vertical_zero = Attribute('vertical_zero', representation_code=RepC.ASCII)
        self.permanent_datum_elevation = NumericAttribute('permanent_datum_elevation', representation_code=RepC.FDOUBL)
        self.above_permanent_datum = NumericAttribute('above_permanent_datum', representation_code=RepC.FDOUBL)
        self.magnetic_declination = NumericAttribute('magnetic_declination', representation_code=RepC.FDOUBL)
        self.coordinate_1_name = Attribute('coordinate_1_name', representation_code=RepC.ASCII)
        self.coordinate_1_value = NumericAttribute('coordinate_1_value', representation_code=RepC.FDOUBL)
        self.coordinate_2_name = Attribute('coordinate_2_name', representation_code=RepC.ASCII)
        self.coordinate_2_value = NumericAttribute('coordinate_2_value', representation_code=RepC.FDOUBL)
        self.coordinate_3_name = Attribute('coordinate_3_name', representation_code=RepC.ASCII)
        self.coordinate_3_value = NumericAttribute('coordinate_3_value', representation_code=RepC.FDOUBL)

        self.set_attributes(**kwargs)
