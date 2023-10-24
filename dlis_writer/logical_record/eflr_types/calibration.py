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
        self.axis = EFLRListAttribute('axis', object_class=Axis)
        self.measurement = ListAttribute('measurement', converter=Attribute.convert_numeric)
        self.sample_count = Attribute('sample_count', converter=int)
        self.maximum_deviation = Attribute('maximum_deviation', converter=float)
        self.standard_deviation = Attribute('standard_deviation', converter=float)
        self.begin_time = DTimeAttribute('begin_time', allow_float=True)
        self.duration = Attribute('duration', converter=float)
        self.reference = ListAttribute('reference', converter=Attribute.convert_numeric)
        self.standard = ListAttribute('standard', converter=Attribute.convert_numeric)
        self.plus_tolerance = ListAttribute('plus_tolerance', converter=Attribute.convert_numeric)
        self.minus_tolerance = ListAttribute('minus_tolerance', converter=Attribute.convert_numeric)

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
        self.coefficients = ListAttribute('coefficients', converter=Attribute.convert_numeric)
        self.references = ListAttribute('references', converter=Attribute.convert_numeric)
        self.plus_tolerances = ListAttribute('plus_tolerances', converter=Attribute.convert_numeric)
        self.minus_tolerances = ListAttribute('minus_tolerances', converter=Attribute.convert_numeric)

        self.set_attributes(**kwargs)


class Calibration(EFLR):
    set_type = 'CALIBRATION'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.calibrated_channels = EFLRListAttribute('calibrated_channels', object_class=Channel)
        self.uncalibrated_channels = EFLRListAttribute('uncalibrated_channels', object_class=Channel)
        self.coefficients = EFLRListAttribute('coefficients', object_class=CalibrationCoefficient)
        self.measurements = EFLRListAttribute('measurements', object_class=CalibrationMeasurement)
        self.parameters = EFLRListAttribute('parameters', object_class=Parameter)
        self.method = Attribute('method', representation_code=RepC.IDENT)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        for attr in (obj.calibrated_channels, obj.uncalibrated_channels, obj.coefficients, obj.measurements,
                     obj.parameters):
            attr.finalise_from_config(config)

        return obj

