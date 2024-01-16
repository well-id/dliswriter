import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import EFLRAttribute, TextAttribute, IdentAttribute


logger = logging.getLogger(__name__)


class GroupItem(EFLRItem):
    """Model an object being part of Group EFLR."""

    parent: "GroupSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise GroupItem.

        Args:
            name        :   Name of the GroupItem.
            parent      :   Group EFLR instance this GroupItem belongs to.
            **kwargs    :   Values of to be set as characteristics of the GroupItem Attributes.
        """

        self.description = TextAttribute('description', parent_eflr=self)
        self.object_type = IdentAttribute('object_type', parent_eflr=self)
        self.object_list = EFLRAttribute('object_list', multivalued=True, parent_eflr=self)
        self.group_list = EFLRAttribute('group_list', object_class=GroupSet, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class GroupSet(EFLRSet):
    """Model Group EFLR."""

    set_type = 'GROUP'
    logical_record_type = EFLRType.STATIC
    item_type = GroupItem


GroupItem.parent_eflr_class = GroupSet
