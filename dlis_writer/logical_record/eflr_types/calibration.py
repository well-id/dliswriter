import logging

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.core.attribute import *


logger = logging.getLogger(__name__)


class CalibrationMeasurementObject(EFLRObject):
    def __init__(self, name: str, parent: "CalibrationMeasurement", **kwargs):

        self.phase = Attribute('phase', representation_code=RepC.IDENT, parent_eflr=self)
        self.measurement_source = EFLRAttribute(
            'measurement_source', representation_code=RepC.OBJREF, object_class=Channel, parent_eflr=self)
        self._type = Attribute('_type', representation_code=RepC.IDENT, parent_eflr=self)
        self.dimension = DimensionAttribute('dimension', parent_eflr=self)
        self.axis = EFLRAttribute('axis', object_class=Axis, multivalued=True, parent_eflr=self)
        self.measurement = NumericAttribute('measurement', multivalued=True, parent_eflr=self)
        self.sample_count = NumericAttribute('sample_count', int_only=True, parent_eflr=self)
        self.maximum_deviation = NumericAttribute('maximum_deviation', parent_eflr=self)
        self.standard_deviation = NumericAttribute('standard_deviation', parent_eflr=self)
        self.begin_time = DTimeAttribute('begin_time', allow_float=True, parent_eflr=self)
        self.duration = NumericAttribute('duration', parent_eflr=self)
        self.reference = NumericAttribute('reference', multivalued=True, parent_eflr=self)
        self.standard = NumericAttribute('standard', multivalued=True, parent_eflr=self)
        self.plus_tolerance = NumericAttribute('plus_tolerance', multivalued=True, parent_eflr=self)
        self.minus_tolerance = NumericAttribute('minus_tolerance', multivalued=True, parent_eflr=self)

        super().__init__(name, parent, **kwargs)


class CalibrationMeasurement(EFLR):
    set_type = 'CALIBRATION-MEASUREMENT'
    logical_record_type = EFLRType.STATIC
    object_type = CalibrationMeasurementObject


class CalibrationCoefficientObject(EFLRObject):

    def __init__(self, name: str, parent: "CalibrationCoefficient", **kwargs):

        self.label = Attribute('label', representation_code=RepC.IDENT, parent_eflr=self)
        self.coefficients = NumericAttribute('coefficients', multivalued=True, parent_eflr=self)
        self.references = NumericAttribute('references', multivalued=True, parent_eflr=self)
        self.plus_tolerances = NumericAttribute('plus_tolerances', multivalued=True, parent_eflr=self)
        self.minus_tolerances = NumericAttribute('minus_tolerances', multivalued=True, parent_eflr=self)

        super().__init__(name, parent, **kwargs)


class CalibrationCoefficient(EFLR):
    set_type = 'CALIBRATION-COEFFICIENT'
    logical_record_type = EFLRType.STATIC
    object_type = CalibrationCoefficientObject


class CalibrationObject(EFLRObject):

    def __init__(self, name: str, parent: "Calibration", **kwargs):

        self.calibrated_channels = EFLRAttribute(
            'calibrated_channels', object_class=Channel, multivalued=True, parent_eflr=self)
        self.uncalibrated_channels = EFLRAttribute(
            'uncalibrated_channels', object_class=Channel, multivalued=True, parent_eflr=self)
        self.coefficients = EFLRAttribute(
            'coefficients', object_class=CalibrationCoefficient, multivalued=True, parent_eflr=self)
        self.measurements = EFLRAttribute(
            'measurements', object_class=CalibrationMeasurement, multivalued=True, parent_eflr=self)
        self.parameters = EFLRAttribute('parameters', object_class=Parameter, multivalued=True, parent_eflr=self)
        self.method = Attribute('method', representation_code=RepC.IDENT, parent_eflr=self)

        super().__init__(name, parent, **kwargs)


class Calibration(EFLR):
    set_type = 'CALIBRATION'
    logical_record_type = EFLRType.STATIC
    object_type = CalibrationObject
