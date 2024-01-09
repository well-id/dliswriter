import logging

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.logical_record.eflr_types.equipment import EquipmentSet
from dlis_writer.logical_record.eflr_types.channel import ChannelSet
from dlis_writer.logical_record.eflr_types.parameter import ParameterSet
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute, StatusAttribute


logger = logging.getLogger(__name__)


class ToolItem(EFLRItem):
    """Model an object being part of Tool EFLR."""

    parent: "ToolSet"

    def __init__(self, name: str, **kwargs):
        """Initialise ToolItem.

        Args:
            name        :   Name of the ToolItem.
            **kwargs    :   Values of to be set as characteristics of the ToolItem Attributes.
        """

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.generic_name = Attribute('generic_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.parts = EFLRAttribute('parts', object_class=EquipmentSet, multivalued=True, parent_eflr=self)
        self.status = StatusAttribute('status', parent_eflr=self)
        self.channels = EFLRAttribute('channels', object_class=ChannelSet, multivalued=True, parent_eflr=self)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterSet, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class ToolSet(EFLRSet):
    """Model Tool EFLR."""

    set_type = 'TOOL'
    logical_record_type = EFLRType.STATIC
    item_type = ToolItem


ToolItem.parent_eflr_class = ToolSet
