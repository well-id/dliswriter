from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class WellReferencePoint(EFLR):
    set_type = 'WELL-REFERENCE'
    logical_record_type = LogicalRecordType.OLR

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.permanent_datum = self._create_attribute('permanent_datum')
        self.vertical_zero = self._create_attribute('vertical_zero')
        self.permanent_datum_elevation = self._create_attribute('permanent_datum_elevation', converter=float)
        self.above_permanent_datum = self._create_attribute('above_permanent_datum', converter=float)
        self.magnetic_declination = self._create_attribute('magnetic_declination', converter=float)
        self.coordinate_1_name = self._create_attribute('coordinate_1_name')
        self.coordinate_1_value = self._create_attribute('coordinate_1_value', converter=float)
        self.coordinate_2_name = self._create_attribute('coordinate_2_name')
        self.coordinate_2_value = self._create_attribute('coordinate_2_value', converter=float)
        self.coordinate_3_name = self._create_attribute('coordinate_3_name')
        self.coordinate_3_value = self._create_attribute('coordinate_3_value', converter=float)

        self.set_attributes(**kwargs)
