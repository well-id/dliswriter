import logging

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute


logger = logging.getLogger(__name__)


class GroupObject(EFLRObject):
    """Model an object being part of Group EFLR."""

    parent: "Group"

    def __init__(self, name: str, **kwargs):
        """Initialise GroupObject.

        Args:
            name        :   Name of the GroupObject.
            parent      :   Group EFLR instance this GroupObject belongs to.
            **kwargs    :   Values of to be set as characteristics of the GroupObject Attributes.
        """

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.object_type = Attribute('object_type', representation_code=RepC.IDENT, parent_eflr=self)
        self.object_list = EFLRAttribute('object_list', multivalued=True, parent_eflr=self)
        self.group_list = EFLRAttribute('group_list', object_class=Group, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class Group(EFLR):
    """Model Group EFLR."""

    set_type = 'GROUP'
    logical_record_type = EFLRType.STATIC
    object_type = GroupObject


GroupObject.parent_eflr_class = Group
