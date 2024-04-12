import logging
from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem, DimensionedItem
from dliswriter.utils.internal_enums import EFLRType, RepresentationCode as RepC
from dliswriter.utils.enums import CalibrationMeasurementPhase
from dliswriter.logical_record.eflr_types.axis import AxisSet
from dliswriter.logical_record.core.attribute import (EFLRAttribute, NumericAttribute,
                                                      DTimeAttribute, DimensionAttribute, IdentAttribute)
from dliswriter.utils.value_checkers import validate_string


logger = logging.getLogger(__name__)


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
            converter=CalibrationMeasurementPhase.make_converter('phases', allow_none=True)
        )
        self.measurement_source = EFLRAttribute(
            'measurement_source', representation_code=RepC.OBJREF, object_class=EFLRSet)
        self.type = IdentAttribute('type', converter=validate_string)
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

        value_counts = self.count_attributes(*controlled_attrs)

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


CalibrationMeasurementItem.parent_eflr_class = CalibrationMeasurementSet
