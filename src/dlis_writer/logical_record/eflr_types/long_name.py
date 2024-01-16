from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import TextAttribute


class LongNameItem(EFLRItem):
    """Model an object being part of LongName EFLR."""

    parent: "LongNameSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise LongNameItem.

        Args:
            name        :   Name of the LongNameItem.
            **kwargs    :   Values of to be set as characteristics of the LongNameItem Attributes.
        """

        self.general_modifier = TextAttribute('general_modifier', multivalued=True, parent_eflr=self)
        self.quantity = TextAttribute('quantity', parent_eflr=self)
        self.quantity_modifier = TextAttribute('quantity_modifier', multivalued=True, parent_eflr=self)
        self.altered_form = TextAttribute('altered_form', parent_eflr=self)
        self.entity = TextAttribute('entity', parent_eflr=self)
        self.entity_modifier = TextAttribute('entity_modifier', multivalued=True, parent_eflr=self)
        self.entity_number = TextAttribute('entity_number', parent_eflr=self)
        self.entity_part = TextAttribute('entity_part', parent_eflr=self)
        self.entity_part_number = TextAttribute('entity_part_number', parent_eflr=self)
        self.generic_source = TextAttribute('generic_source', parent_eflr=self)
        self.source_part = TextAttribute('source_part', multivalued=True, parent_eflr=self)
        self.source_part_number = TextAttribute('source_part_number', multivalued=True, parent_eflr=self)
        self.conditions = TextAttribute('conditions', multivalued=True, parent_eflr=self)
        self.standard_symbol = TextAttribute('standard_symbol', parent_eflr=self)
        self.private_symbol = TextAttribute('private_symbol', parent_eflr=self)

        super().__init__(name, **kwargs)


class LongNameSet(EFLRSet):
    """Model LongName EFLR."""

    set_type = 'LONG-NAME'
    logical_record_type = EFLRType.LNAME
    item_type = LongNameItem


LongNameItem.parent_eflr_class = LongNameSet
