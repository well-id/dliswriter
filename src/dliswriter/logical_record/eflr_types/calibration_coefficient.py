import logging
from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.utils.internal_enums import EFLRType
from dliswriter.logical_record.core.attribute import NumericAttribute, IdentAttribute
from dliswriter.utils.value_checkers import validate_string


logger = logging.getLogger(__name__)


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

        self.label = IdentAttribute('label', converter=validate_string)
        self.coefficients = NumericAttribute('coefficients', multivalued=True)
        self.references = NumericAttribute('references', multivalued=True)
        self.plus_tolerances = NumericAttribute('plus_tolerances', multivalued=True)
        self.minus_tolerances = NumericAttribute('minus_tolerances', multivalued=True)

        super().__init__(name, parent=parent, **kwargs)

    def _run_checks_and_set_defaults(self) -> None:
        """Check that the number of coefficients, references, and tolerances is equal."""

        value_counts = self.count_attributes(
            self.coefficients, self.references, self.plus_tolerances, self.minus_tolerances)

        if len(set(value_counts.values())) > 1:
            raise RuntimeError(f"Number of values all numeric attributes of Calibration Coefficient should be equal; "
                               f"got {', '.join('{} for {}'.format(v, k) for k, v in value_counts.items())}")


class CalibrationCoefficientSet(EFLRSet):
    """Model CalibrationCoefficient EFLR."""

    set_type = 'CALIBRATION-COEFFICIENT'
    logical_record_type = EFLRType.STATIC
    item_type = CalibrationCoefficientItem


CalibrationCoefficientItem.parent_eflr_class = CalibrationCoefficientSet
