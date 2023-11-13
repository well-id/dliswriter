import logging

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute


logger = logging.getLogger(__name__)


class GroupObject(EFLRObject):

    def __init__(self, name: str, parent: "Group", **kwargs):

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.object_type = Attribute('object_type', representation_code=RepC.IDENT, parent_eflr=self)
        self.object_list = EFLRAttribute('object_list', multivalued=True, parent_eflr=self)
        self.group_list = EFLRAttribute('group_list', object_class=Group, multivalued=True, parent_eflr=self)

        super().__init__(name, parent, **kwargs)


class Group(EFLR):
    set_type = 'GROUP'
    logical_record_type = EFLRType.STATIC
    object_type = GroupObject
