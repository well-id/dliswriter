import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.logical_record.eflr_types.axis import Axis


logger = logging.getLogger(__name__)


class CalibrationMeasurement(EFLR):
    set_type = 'CALIBRATION-MEASUREMENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        conv = lambda val: self.convert_values(val, require_numeric=True)

        self.phase = self._create_attribute('phase', representation_code=RepC.IDENT)
        self.measurement_source = self._create_attribute('measurement_source', representation_code=RepC.OBJREF)
        self._type = self._create_attribute('_type', representation_code=RepC.IDENT)
        self.dimension = self._create_attribute(
            'dimension', converter=self.convert_dimension_or_el_limit,
            multivalued=True, representation_code=RepC.UVARI)
        self.axis = self._create_attribute('axis', multivalued=True, representation_code=RepC.OBNAME)
        self.measurement = self._create_attribute('measurement', converter=conv, multivalued=True)
        self.sample_count = self._create_attribute('sample_count', converter=conv)
        self.maximum_deviation = self._create_attribute('maximum_deviation', converter=conv)
        self.standard_deviation = self._create_attribute('standard_deviation', converter=conv)
        self.begin_time = self._create_attribute('begin_time', converter=self.parse_dtime)
        self.duration = self._create_attribute('duration', converter=float)
        self.reference = self._create_attribute('reference', converter=conv, multivalued=True)
        self.standard = self._create_attribute('standard', converter=conv, multivalued=True)
        self.plus_tolerance = self._create_attribute('plus_tolerance', converter=conv, multivalued=True)
        self.minus_tolerance = self._create_attribute('minus_tolerance', converter=conv, multivalued=True)

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

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        conv = lambda val: self.convert_values(val, require_numeric=True)

        self.label = self._create_attribute('label', representation_code=RepC.IDENT)
        self.coefficients = self._create_attribute('coefficients', converter=conv, multivalued=True)
        self.references = self._create_attribute('references', converter=conv, multivalued=True)
        self.plus_tolerances = self._create_attribute('plus_tolerances', converter=conv, multivalued=True)
        self.minus_tolerances = self._create_attribute('minus_tolerances', converter=conv, multivalued=True)

        self.set_attributes(**kwargs)


class Calibration(EFLR):
    set_type = 'CALIBRATION'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.calibrated_channels = self._create_attribute(
            'calibrated_channels', multivalued=True, representation_code=RepC.OBNAME)
        self.uncalibrated_channels = self._create_attribute(
            'uncalibrated_channels', multivalued=True, representation_code=RepC.OBNAME)
        self.coefficients = self._create_attribute(
            'coefficients', multivalued=True, representation_code=RepC.OBNAME)
        self.measurements = self._create_attribute(
            'measurements', multivalued=True, representation_code=RepC.OBNAME)
        self.parameters = self._create_attribute(
            'parameters', multivalued=True, representation_code=RepC.OBNAME)
        self.method = self._create_attribute('method', representation_code=RepC.IDENT)

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

