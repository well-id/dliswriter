from .utils.core import EFLR


class CalibrationMeasurement(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'
        self.set_type = 'CALIBRATION-MEASUREMENT'

        self.phase = None
        self.measurement_source = None
        self._type = None
        self.dimension = None
        self.axis = None
        self.measurement = None
        self.sample_count = None
        self.maximum_deviation = None
        self.standard_deviation = None
        self.begin_time = None
        self.duration = None
        self.reference = None
        self.standard = None
        self.plus_tolerance = None
        self.minus_tolerance = None

        self.create_attributes()


class CalibrationCoefficient(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'
        self.set_type = 'CALIBRATION-COEFFICIENT'

        self.label = None
        self.coefficients = None
        self.references = None
        self.plus_tolerances = None
        self.minus_tolerances = None

        self.create_attributes()


class Calibration(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'
        self.set_type = 'CALIBRATION'

        self.calibrated_channels = None
        self.uncalibrated_channels = None
        self.coefficients = None
        self.measurements = None
        self.parameters = None
        self.method = None

        self.create_attributes()