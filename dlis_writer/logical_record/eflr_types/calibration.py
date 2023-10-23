import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.core.attribute import Attribute


logger = logging.getLogger(__name__)


class CalibrationMeasurement(EFLR):
    set_type = 'CALIBRATION-MEASUREMENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        conv = lambda val: self.convert_values(val, require_numeric=True)

        self.phase = Attribute('phase', representation_code=RepC.IDENT)
        self.measurement_source = Attribute('measurement_source', representation_code=RepC.OBJREF)
        self._type = Attribute('_type', representation_code=RepC.IDENT)
        self.dimension = Attribute(
            'dimension', converter=self.convert_dimension_or_el_limit,
            multivalued=True, representation_code=RepC.UVARI)
        self.axis = Attribute('axis', multivalued=True, representation_code=RepC.OBNAME)
        self.measurement = Attribute('measurement', converter=conv, multivalued=True)
        self.sample_count = Attribute('sample_count', converter=conv)
        self.maximum_deviation = Attribute('maximum_deviation', converter=conv)
        self.standard_deviation = Attribute('standard_deviation', converter=conv)
        self.begin_time = Attribute('begin_time', converter=self.parse_dtime)
        self.duration = Attribute('duration', converter=float)
        self.reference = Attribute('reference', converter=conv, multivalued=True)
        self.standard = Attribute('standard', converter=conv, multivalued=True)
        self.plus_tolerance = Attribute('plus_tolerance', converter=conv, multivalued=True)
        self.minus_tolerance = Attribute('minus_tolerance', converter=conv, multivalued=True)

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

        self.label = Attribute('label', representation_code=RepC.IDENT)
        self.coefficients = Attribute('coefficients', converter=conv, multivalued=True)
        self.references = Attribute('references', converter=conv, multivalued=True)
        self.plus_tolerances = Attribute('plus_tolerances', converter=conv, multivalued=True)
        self.minus_tolerances = Attribute('minus_tolerances', converter=conv, multivalued=True)

        self.set_attributes(**kwargs)


class Calibration(EFLR):
    set_type = 'CALIBRATION'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.calibrated_channels = Attribute(
            'calibrated_channels', multivalued=True, representation_code=RepC.OBNAME)
        self.uncalibrated_channels = Attribute(
            'uncalibrated_channels', multivalued=True, representation_code=RepC.OBNAME)
        self.coefficients = Attribute(
            'coefficients', multivalued=True, representation_code=RepC.OBNAME)
        self.measurements = Attribute(
            'measurements', multivalued=True, representation_code=RepC.OBNAME)
        self.parameters = Attribute(
            'parameters', multivalued=True, representation_code=RepC.OBNAME)
        self.method = Attribute('method', representation_code=RepC.IDENT)

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

