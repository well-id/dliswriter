import logging
from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.utils.internal.internal_enums import EFLRType
from dliswriter.logical_record.eflr_types.channel import ChannelSet
from dliswriter.logical_record.eflr_types.parameter import ParameterSet
from dliswriter.logical_record.eflr_types.calibration_measurement import CalibrationMeasurementSet
from dliswriter.logical_record.eflr_types.calibration_coefficient import CalibrationCoefficientSet
from dliswriter.logical_record.core.attribute import EFLRAttribute, IdentAttribute


logger = logging.getLogger(__name__)


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


CalibrationItem.parent_eflr_class = CalibrationSet
