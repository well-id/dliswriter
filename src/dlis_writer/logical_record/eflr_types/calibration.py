import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.channel import ChannelSet
from dlis_writer.logical_record.eflr_types.parameter import ParameterSet
from dlis_writer.logical_record.eflr_types.axis import AxisSet
from dlis_writer.logical_record.core.attribute import (EFLRAttribute, NumericAttribute,
                                                       DTimeAttribute, DimensionAttribute, IdentAttribute)


logger = logging.getLogger(__name__)


class CalibrationMeasurementItem(EFLRItem):
    """Model an object being part of CalibrationMeasurement EFLR."""

    parent: "CalibrationMeasurementSet"

    allowed_phases = ('AFTER', 'BEFORE', 'MASTER')

    def __init__(self, name: str, parent: "CalibrationMeasurementSet", **kwargs: Any) -> None:
        """Initialise CalibrationMeasurementItem.

        Args:
            name        :   Name of the CalibrationMeasurementItem.
            parent      :   Parent CalibrationMeasurementSet of this CalibrationMeasurementItem.
            **kwargs    :   Values of to be set as characteristics of the CalibrationMeasurementItem Attributes.
        """

        self.phase = IdentAttribute('phase', converter=self.make_converter_for_allowed_str_values(
            self.allowed_phases, 'phases', allow_none=True, make_uppercase=True))
        self.measurement_source = EFLRAttribute(
            'measurement_source', representation_code=RepC.OBJREF, object_class=EFLRSet)
        self.type = IdentAttribute('type')
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=AxisSet, multivalued=True)
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

        super().__init__(name, parent=parent, **kwargs)


class CalibrationMeasurementSet(EFLRSet):
    """Model CalibrationMeasurement EFLR."""

    set_type = 'CALIBRATION-MEASUREMENT'
    logical_record_type = EFLRType.STATIC
    item_type = CalibrationMeasurementItem


class CalibrationCoefficientItem(EFLRItem):
    """Model an object being part of CalibrationCoefficient EFLR."""

    parent: "CalibrationCoefficientSet"

    def __init__(self, name: str, parent: "CalibrationCoefficientSet", **kwargs: Any) -> None:
        """Initialise CalibrationCoefficientItem.

        Args:
            name        :   Name of the CalibrationCoefficientItem.
            parent      :   Parent CalibrationCoefficientSet of this CalibrationCoefficientItem.
            **kwargs    :   Values of to be set as characteristics of the CalibrationCoefficientItem Attributes.
        """

        self.label = IdentAttribute('label')
        self.coefficients = NumericAttribute('coefficients', multivalued=True)
        self.references = NumericAttribute('references', multivalued=True)
        self.plus_tolerances = NumericAttribute('plus_tolerances', multivalued=True)
        self.minus_tolerances = NumericAttribute('minus_tolerances', multivalued=True)

        super().__init__(name, parent=parent, **kwargs)


class CalibrationCoefficientSet(EFLRSet):
    """Model CalibrationCoefficient EFLR."""

    set_type = 'CALIBRATION-COEFFICIENT'
    logical_record_type = EFLRType.STATIC
    item_type = CalibrationCoefficientItem


class CalibrationItem(EFLRItem):
    """Model an object being part of Calibration EFLR."""

    parent: "CalibrationSet"

    def __init__(self, name: str, parent: "CalibrationSet", **kwargs: Any) -> None:
        """Initialise CalibrationItem.

        Args:
            name        :   Name of the CalibrationItem.
            parent      :   Parent CalibrationSet of this CalibrationItem.
            **kwargs    :   Values of to be set as characteristics of the CalibrationItem Attributes.
        """

        self.calibrated_channels = EFLRAttribute(
            'calibrated_channels', object_class=ChannelSet, multivalued=True)
        self.uncalibrated_channels = EFLRAttribute(
            'uncalibrated_channels', object_class=ChannelSet, multivalued=True)
        self.coefficients = EFLRAttribute(
            'coefficients', object_class=CalibrationCoefficientSet, multivalued=True)
        self.measurements = EFLRAttribute(
            'measurements', object_class=CalibrationMeasurementSet, multivalued=True)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterSet, multivalued=True)
        self.method = IdentAttribute('method')

        super().__init__(name, parent=parent, **kwargs)


class CalibrationSet(EFLRSet):
    """Model Calibration EFLR."""

    set_type = 'CALIBRATION'
    logical_record_type = EFLRType.STATIC
    item_type = CalibrationItem


CalibrationMeasurementItem.parent_eflr_class = CalibrationMeasurementSet
CalibrationCoefficientItem.parent_eflr_class = CalibrationCoefficientSet
CalibrationItem.parent_eflr_class = CalibrationSet
