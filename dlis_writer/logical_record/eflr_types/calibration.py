import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.logical_record.eflr_types.axis import Axis


logger = logging.getLogger(__name__)


class CalibrationMeasurement(EFLR):
    set_type = 'CALIBRATION-MEASUREMENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        conv = lambda val: self.convert_values(val, require_numeric=True)

        self.phase = self._create_attribute('phase')
        self.measurement_source = self._create_attribute('measurement_source')
        self._type = self._create_attribute('_type')
        self.dimension = self._create_attribute('dimension', converter=self.convert_dimension_or_el_limit)
        self.axis = self._create_attribute('axis')
        self.measurement = self._create_attribute('measurement', converter=conv)
        self.sample_count = self._create_attribute('sample_count', converter=conv)
        self.maximum_deviation = self._create_attribute('maximum_deviation', converter=conv)
        self.standard_deviation = self._create_attribute('standard_deviation', converter=conv)
        self.begin_time = self._create_attribute('begin_time', converter=self.parse_dtime)
        self.duration = self._create_attribute('duration', converter=float)
        self.reference = self._create_attribute('reference', converter=conv)
        self.standard = self._create_attribute('standard', converter=conv)
        self.plus_tolerance = self._create_attribute('plus_tolerance', converter=conv)
        self.minus_tolerance = self._create_attribute('minus_tolerance', converter=conv)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'measurement_source', Channel, single=True)
        obj.add_dependent_objects_from_config(config, 'axis', Axis)

        return obj


class CalibrationCoefficient(EFLR):
    set_type = 'CALIBRATION-COEFFICIENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        conv = lambda val: self.convert_values(val, require_numeric=True)

        self.label = self._create_attribute('label')
        self.coefficients = self._create_attribute('coefficients', converter=conv)
        self.references = self._create_attribute('references', converter=conv)
        self.plus_tolerances = self._create_attribute('plus_tolerances', converter=conv)
        self.minus_tolerances = self._create_attribute('minus_tolerances', converter=conv)

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

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'calibrated_channels', Channel)
        obj.add_dependent_objects_from_config(config, 'uncalibrated_channels', Channel)
        obj.add_dependent_objects_from_config(config, 'measurements', CalibrationMeasurement)
        obj.add_dependent_objects_from_config(config, 'coefficients', CalibrationCoefficient)
        obj.add_dependent_objects_from_config(config, 'parameters', Parameter)

        return obj

