import logging

from dlis_writer.logical_record.core.eflr import EFLRTable, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute


logger = logging.getLogger(__name__)


class GroupItem(EFLRItem):
    """Model an object being part of Group EFLR."""

    parent: "GroupTable"

    def __init__(self, name: str, **kwargs):
        """Initialise GroupItem.

        Args:
            name        :   Name of the GroupItem.
            parent      :   Group EFLR instance this GroupItem belongs to.
            **kwargs    :   Values of to be set as characteristics of the GroupItem Attributes.
        """

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.object_type = Attribute('object_type', representation_code=RepC.IDENT, parent_eflr=self)
        self.object_list = EFLRAttribute('object_list', multivalued=True, parent_eflr=self)
        self.group_list = EFLRAttribute('group_list', object_class=GroupTable, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class GroupTable(EFLRTable):
    """Model Group EFLR."""

    set_type = 'GROUP'
    logical_record_type = EFLRType.STATIC
    item_type = GroupItem


GroupItem.parent_eflr_class = GroupTable
