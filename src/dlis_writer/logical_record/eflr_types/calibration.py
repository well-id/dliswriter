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

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise CalibrationMeasurementItem.

        Args:
            name        :   Name of the CalibrationMeasurementItem.
            **kwargs    :   Values of to be set as characteristics of the CalibrationMeasurementItem Attributes.
        """

        self.phase = IdentAttribute('phase', parent_eflr=self)
        self.measurement_source = EFLRAttribute(
            'measurement_source', representation_code=RepC.OBJREF, object_class=ChannelSet, parent_eflr=self)
        self._type = IdentAttribute('_type', parent_eflr=self)
        self.dimension = DimensionAttribute('dimension', parent_eflr=self)
        self.axis = EFLRAttribute('axis', object_class=AxisSet, multivalued=True, parent_eflr=self)
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

        super().__init__(name, **kwargs)


class CalibrationMeasurementSet(EFLRSet):
    """Model CalibrationMeasurement EFLR."""

    set_type = 'CALIBRATION-MEASUREMENT'
    logical_record_type = EFLRType.STATIC
    item_type = CalibrationMeasurementItem


class CalibrationCoefficientItem(EFLRItem):
    """Model an object being part of CalibrationCoefficient EFLR."""

    parent: "CalibrationCoefficientSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise CalibrationCoefficientItem.

        Args:
            name        :   Name of the CalibrationCoefficientItem.
            **kwargs    :   Values of to be set as characteristics of the CalibrationCoefficientItem Attributes.
        """

        self.label = IdentAttribute('label', parent_eflr=self)
        self.coefficients = NumericAttribute('coefficients', multivalued=True, parent_eflr=self)
        self.references = NumericAttribute('references', multivalued=True, parent_eflr=self)
        self.plus_tolerances = NumericAttribute('plus_tolerances', multivalued=True, parent_eflr=self)
        self.minus_tolerances = NumericAttribute('minus_tolerances', multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class CalibrationCoefficientSet(EFLRSet):
    """Model CalibrationCoefficient EFLR."""

    set_type = 'CALIBRATION-COEFFICIENT'
    logical_record_type = EFLRType.STATIC
    item_type = CalibrationCoefficientItem


class CalibrationItem(EFLRItem):
    """Model an object being part of Calibration EFLR."""

    parent: "CalibrationSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise CalibrationItem.

        Args:
            name        :   Name of the CalibrationItem.
            **kwargs    :   Values of to be set as characteristics of the CalibrationItem Attributes.
        """

        self.calibrated_channels = EFLRAttribute(
            'calibrated_channels', object_class=ChannelSet, multivalued=True, parent_eflr=self)
        self.uncalibrated_channels = EFLRAttribute(
            'uncalibrated_channels', object_class=ChannelSet, multivalued=True, parent_eflr=self)
        self.coefficients = EFLRAttribute(
            'coefficients', object_class=CalibrationCoefficientSet, multivalued=True, parent_eflr=self)
        self.measurements = EFLRAttribute(
            'measurements', object_class=CalibrationMeasurementSet, multivalued=True, parent_eflr=self)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterSet, multivalued=True, parent_eflr=self)
        self.method = IdentAttribute('method', parent_eflr=self)

        super().__init__(name, **kwargs)


class CalibrationSet(EFLRSet):
    """Model Calibration EFLR."""

    set_type = 'CALIBRATION'
    logical_record_type = EFLRType.STATIC
    item_type = CalibrationItem


CalibrationMeasurementItem.parent_eflr_class = CalibrationMeasurementSet
CalibrationCoefficientItem.parent_eflr_class = CalibrationCoefficientSet
CalibrationItem.parent_eflr_class = CalibrationSet
