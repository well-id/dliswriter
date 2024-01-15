from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


class NoFormatItem(EFLRItem):
    """Model an object being part of NoFormat EFLR."""

    parent: "NoFormatSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise NoFormatItem.

        Args:
            name        :   Name of the NoFormatItem.
            **kwargs    :   Values of to be set as characteristics of the NoFormatItem Attributes.
        """

        self.consumer_name = Attribute('consumer_name', representation_code=RepC.IDENT, parent_eflr=self)
        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)

        super().__init__(name, **kwargs)


class NoFormatSet(EFLRSet):
    """Model NoFormat EFLR."""

    set_type = 'NO-FORMAT'
    logical_record_type = EFLRType.UDI
    item_type = NoFormatItem


NoFormatItem.parent_eflr_class = NoFormatSet
