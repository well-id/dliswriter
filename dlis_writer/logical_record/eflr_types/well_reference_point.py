from dlis_writer.logical_record.core import EFLR


class WellReferencePoint(EFLR):
    set_type = 'WELL-REFERENCE'
    logical_record_type = 'OLR'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.permanent_datum = None
        self.vertical_zero = None
        self.permanent_datum_elevation = None
        self.above_permanent_datum = None
        self.magnetic_declination = None
        self.coordinate_1_name = None
        self.coordinate_1_value = None
        self.coordinate_2_name = None
        self.coordinate_2_value = None
        self.coordinate_3_name = None
        self.coordinate_3_value = None

        self.attributes = self.create_attributes()
