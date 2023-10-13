from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class CalibrationMeasurement(EFLR):
    set_type = 'CALIBRATION-MEASUREMENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.phase = self._create_attribute('phase')
        self.measurement_source = self._create_attribute('measurement_source')
        self._type = self._create_attribute('_type')
        self.dimension = self._create_attribute('dimension')
        self.axis = self._create_attribute('axis')
        self.measurement = self._create_attribute('measurement')
        self.sample_count = self._create_attribute('sample_count')
        self.maximum_deviation = self._create_attribute('maximum_deviation')
        self.standard_deviation = self._create_attribute('standard_deviation')
        self.begin_time = self._create_attribute('begin_time')
        self.duration = self._create_attribute('duration')
        self.reference = self._create_attribute('reference')
        self.standard = self._create_attribute('standard')
        self.plus_tolerance = self._create_attribute('plus_tolerance')
        self.minus_tolerance = self._create_attribute('minus_tolerance')

        self.set_attributes(**kwargs)


class CalibrationCoefficient(EFLR):
    set_type = 'CALIBRATION-COEFFICIENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.label = self._create_attribute('label')
        self.coefficients = self._create_attribute('coefficients')
        self.references = self._create_attribute('references')
        self.plus_tolerances = self._create_attribute('plus_tolerances')
        self.minus_tolerances = self._create_attribute('minus_tolerances')

        self.set_attributes(**kwargs)


class Calibration(EFLR):
    set_type = 'CALIBRATION'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):

        super().__init__(object_name, set_name)

        self.calibrated_channels = self._create_attribute('calibrated_channels')
        self.uncalibrated_channels = self._create_attribute('uncalibrated_channels')
        self.coefficients = self._create_attribute('coefficients')
        self.measurements = self._create_attribute('measurements')
        self.parameters = self._create_attribute('parameters')
        self.method = self._create_attribute('method')

        self.set_attributes(**kwargs)
