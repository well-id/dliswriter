import logging
from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.utils.internal_enums import EFLRType, RepresentationCode as RepC
from dliswriter.logical_record.core.attribute import EFLRAttribute, TextAttribute, IdentAttribute
from dliswriter.utils.value_checkers import validate_string


logger = logging.getLogger(__name__)


class GroupItem(EFLRItem):
    """Model an object being part of Group EFLR."""

    parent: "GroupSet"

    def __init__(self, name: str, parent: "GroupSet", **kwargs: Any) -> None:
        """Initialise GroupItem.

        Args:
            name        :   Name of the GroupItem.
            parent      :   Group EFLRSet instance this GroupItem belongs to.
            **kwargs    :   Values of to be set as characteristics of the GroupItem Attributes.
        """

        self.description = TextAttribute('description')
        self.object_type = IdentAttribute('object_type', converter=validate_string)
        self.object_list = EFLRAttribute('object_list', multivalued=True, representation_code=RepC.OBJREF)
        self.group_list = EFLRAttribute('group_list', object_class=GroupSet, multivalued=True)

        super().__init__(name, parent=parent, **kwargs)


class GroupSet(EFLRSet):
    """Model Group EFLR."""

    set_type = 'GROUP'
    logical_record_type = EFLRType.STATIC
    item_type = GroupItem


GroupItem.parent_eflr_class = GroupSet
