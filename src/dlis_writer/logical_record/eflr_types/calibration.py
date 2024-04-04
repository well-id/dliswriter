import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem, DimensionedItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC, CalibrationMeasurementPhase
from dlis_writer.logical_record.eflr_types.channel import ChannelSet
from dlis_writer.logical_record.eflr_types.parameter import ParameterSet
from dlis_writer.logical_record.eflr_types.axis import AxisSet
from dlis_writer.logical_record.core.attribute import (EFLRAttribute, NumericAttribute, Attribute,
                                                       DTimeAttribute, DimensionAttribute, IdentAttribute)


logger = logging.getLogger(__name__)


def count_attributes(*attrs: Attribute) -> dict:
    # check that the multivalued attributes of the object all have the same number of values - if defined at all
    value_counts = {}
    for attr in attrs:
        if attr.value is not None:
            value_counts[attr.label] = len(attr.value)

    return value_counts


class CalibrationMeasurementItem(EFLRItem, DimensionedItem):
    """Model an object being part of CalibrationMeasurement EFLR."""

    parent: "CalibrationMeasurementSet"

    def __init__(self, name: str, parent: "CalibrationMeasurementSet", **kwargs: Any) -> None:
        """Initialise CalibrationMeasurementItem.

        Args:
            name        :   Name of the CalibrationMeasurementItem.
            parent      :   Parent CalibrationMeasurementSet of this CalibrationMeasurementItem.
            **kwargs    :   Values of to be set as characteristics of the CalibrationMeasurementItem Attributes.
        """

        self.phase = IdentAttribute(
            'phase',
            converter=CalibrationMeasurementPhase.make_converter('phases', allow_none=True, make_uppercase=True)
        )
        self.measurement_source = EFLRAttribute(
            'measurement_source', representation_code=RepC.OBJREF, object_class=EFLRSet)
        self.type = IdentAttribute('type')
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=AxisSet, multivalued=True)
        self.measurement = NumericAttribute('measurement', multivalued=True, multidimensional=True)
        self.sample_count = NumericAttribute('sample_count', int_only=True)
        self.maximum_deviation = NumericAttribute('maximum_deviation', multivalued=True, multidimensional=True)
        self.standard_deviation = NumericAttribute('standard_deviation', multivalued=True, multidimensional=True)
        self.begin_time = DTimeAttribute('begin_time', allow_float=True)
        self.duration = NumericAttribute('duration')
        self.reference = NumericAttribute('reference', multivalued=True, multidimensional=True)
        self.standard = NumericAttribute('standard', multivalued=True, multidimensional=True)
        self.plus_tolerance = NumericAttribute('plus_tolerance', multivalued=True, multidimensional=True)
        self.minus_tolerance = NumericAttribute('minus_tolerance', multivalued=True, multidimensional=True)

        super().__init__(name, parent=parent, **kwargs)

    def _run_checks_and_set_defaults(self) -> None:
        self._check_axis_vs_dimension()

        controlled_attrs = (self.maximum_deviation, self.standard_deviation, self.standard,
                            self.plus_tolerance, self.minus_tolerance)

        value_counts = count_attributes(*controlled_attrs)

        if len(set(value_counts.values())) > 1:
            raise RuntimeError(f"Number of values all numeric attributes of Calibration Coefficient should be equal; "
                               f"got {', '.join('{} for {}'.format(v, k) for k, v in value_counts.items())}")

        for attr in controlled_attrs:
            self._check_or_set_value_dimensionality(attr.value, value_label=attr.label)


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

    def _run_checks_and_set_defaults(self) -> None:
        value_counts = count_attributes(self.coefficients, self.references, self.plus_tolerances, self.minus_tolerances)

        if len(set(value_counts.values())) > 1:
            raise RuntimeError(f"Number of values all numeric attributes of Calibration Coefficient should be equal; "
                               f"got {', '.join('{} for {}'.format(v, k) for k, v in value_counts.items())}")


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
