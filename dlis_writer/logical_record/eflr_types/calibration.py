import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.core.attribute import *


logger = logging.getLogger(__name__)


class CalibrationMeasurement(EFLR):
    set_type = 'CALIBRATION-MEASUREMENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.phase = Attribute('phase', representation_code=RepC.IDENT)
        self.measurement_source = EFLRAttribute(
            'measurement_source', representation_code=RepC.OBJREF, object_class=Channel)
        self._type = Attribute('_type', representation_code=RepC.IDENT)
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=Axis, multivalued=True)
        self.measurement = NumericAttribute('measurement', multivalued=True)
        self.sample_count = NumericAttribute('sample_count', int_only=True)
        self.maximum_deviation = NumericAttribute('maximum_deviation')
        self.standard_deviation = NumericAttribute('standard_deviation')
        self.begin_time = DTimeAttribute('begin_time', allow_float=True)
        self.duration = NumericAttribute('duration')
        self.reference = NumericAttribute('reference', multivalued=True)
        self.standard = NumericAttribute('standard', multivalued=True)
        self.plus_tolerance = NumericAttribute('plus_tolerance', multivalued=True)
        self.minus_tolerance = NumericAttribute('minus_tolerance', multivalued=True)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        for attr in (obj.measurement_source, obj.axis):
            attr.finalise_from_config(config)

        return obj


class CalibrationCoefficient(EFLR):
    set_type = 'CALIBRATION-COEFFICIENT'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.label = Attribute('label', representation_code=RepC.IDENT)
        self.coefficients = NumericAttribute('coefficients', multivalued=True)
        self.references = NumericAttribute('references', multivalued=True)
        self.plus_tolerances = NumericAttribute('plus_tolerances', multivalued=True)
        self.minus_tolerances = NumericAttribute('minus_tolerances', multivalued=True)

        self.set_attributes(**kwargs)


class Calibration(EFLR):
    set_type = 'CALIBRATION'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.calibrated_channels = EFLRAttribute('calibrated_channels', object_class=Channel, multivalued=True)
        self.uncalibrated_channels = EFLRAttribute('uncalibrated_channels', object_class=Channel, multivalued=True)
        self.coefficients = EFLRAttribute('coefficients', object_class=CalibrationCoefficient, multivalued=True)
        self.measurements = EFLRAttribute('measurements', object_class=CalibrationMeasurement, multivalued=True)
        self.parameters = EFLRAttribute('parameters', object_class=Parameter, multivalued=True)
        self.method = Attribute('method', representation_code=RepC.IDENT)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        for attr in (obj.calibrated_channels, obj.uncalibrated_channels, obj.coefficients, obj.measurements,
                     obj.parameters):
            attr.finalise_from_config(config)

        return obj

