from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.utils.internal.internal_enums import EFLRType
from dliswriter.logical_record.core.attribute import TextAttribute


class LongNameItem(EFLRItem):
    """Model an object being part of LongName EFLR."""

    parent: "LongNameSet"

    def __init__(self, name: str, parent: "LongNameSet", **kwargs: Any) -> None:
        """Initialise LongNameItem.

        Args:
            name        :   Name of the LongNameItem.
            parent      :   Parent LongNameSet of this LongNameItem.
            **kwargs    :   Values of to be set as characteristics of the LongNameItem Attributes.
        """

        self.general_modifier = TextAttribute('general_modifier', multivalued=True)
        self.quantity = TextAttribute('quantity')
        self.quantity_modifier = TextAttribute('quantity_modifier', multivalued=True)
        self.altered_form = TextAttribute('altered_form')
        self.entity = TextAttribute('entity')
        self.entity_modifier = TextAttribute('entity_modifier', multivalued=True)
        self.entity_number = TextAttribute('entity_number')
        self.entity_part = TextAttribute('entity_part')
        self.entity_part_number = TextAttribute('entity_part_number')
        self.generic_source = TextAttribute('generic_source')
        self.source_part = TextAttribute('source_part', multivalued=True)
        self.source_part_number = TextAttribute('source_part_number', multivalued=True)
        self.conditions = TextAttribute('conditions', multivalued=True)
        self.standard_symbol = TextAttribute('standard_symbol')
        self.private_symbol = TextAttribute('private_symbol')

        super().__init__(name, parent=parent, **kwargs)


class LongNameSet(EFLRSet):
    """Model LongName EFLR."""

    set_type = 'LONG-NAME'
    logical_record_type = EFLRType.LNAME
    item_type = LongNameItem


LongNameItem.parent_eflr_class = LongNameSet
