from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.internal_enums import EFLRType
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute, IdentAttribute
from dlis_writer.utils.value_checkers import validate_string, convert_maybe_numeric


class AxisItem(EFLRItem):
    """Model an object being part of Axis EFLR."""

    parent: "AxisSet"

    def __init__(self, name: str, parent: "AxisSet", **kwargs: Any) -> None:
        """Initialise AxisItem.

        Args:
            name        :   Name of the AxisItem.
            parent      :   Parent AxisSet of this AxisItem.
            **kwargs    :   Values of to be set as characteristics of the AxisItem Attributes.
        """

        self.axis_id = IdentAttribute('axis_id', converter=validate_string)
        self.coordinates = Attribute('coordinates', multivalued=True, converter=convert_maybe_numeric)
        self.spacing = NumericAttribute('spacing')

        super().__init__(name, parent=parent, **kwargs)


class AxisSet(EFLRSet):
    """Model Axis EFLR."""

    set_type = 'AXIS'
    logical_record_type = EFLRType.AXIS
    item_type = AxisItem


AxisItem.parent_eflr_class = AxisSet
