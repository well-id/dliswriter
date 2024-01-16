from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute, IdentAttribute


class AxisItem(EFLRItem):
    """Model an object being part of Axis EFLR."""

    parent: "AxisSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise AxisItem.

        Args:
            name        :   Name of the AxisItem.
            **kwargs    :   Values of to be set as characteristics of the AxisItem Attributes.
        """

        self.axis_id = IdentAttribute('axis_id')
        self.coordinates = Attribute('coordinates', multivalued=True, converter=self.convert_maybe_numeric)
        self.spacing = NumericAttribute('spacing')

        super().__init__(name, **kwargs)


class AxisSet(EFLRSet):
    """Model Axis EFLR."""

    set_type = 'AXIS'
    logical_record_type = EFLRType.AXIS
    item_type = AxisItem


AxisItem.parent_eflr_class = AxisSet
