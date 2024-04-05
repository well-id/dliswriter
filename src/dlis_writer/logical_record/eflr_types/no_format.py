from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.internal_enums import EFLRType
from dlis_writer.logical_record.core.attribute import IdentAttribute, TextAttribute


class NoFormatItem(EFLRItem):
    """Model an object being part of NoFormat EFLR."""

    parent: "NoFormatSet"

    def __init__(self, name: str, parent: "NoFormatSet", **kwargs: Any) -> None:
        """Initialise NoFormatItem.

        Args:
            name        :   Name of the NoFormatItem.
            parent      :   Parent NoFormatSet of this NoFormatItem.
            **kwargs    :   Values of to be set as characteristics of the NoFormatItem Attributes.
        """

        self.consumer_name = IdentAttribute('consumer_name')
        self.description = TextAttribute('description')

        super().__init__(name, parent=parent, **kwargs)


class NoFormatSet(EFLRSet):
    """Model NoFormat EFLR."""

    set_type = 'NO-FORMAT'
    logical_record_type = EFLRType.UDI
    item_type = NoFormatItem


NoFormatItem.parent_eflr_class = NoFormatSet
