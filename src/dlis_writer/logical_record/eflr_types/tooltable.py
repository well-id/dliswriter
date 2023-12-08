import logging

from dlis_writer.logical_record.core.eflr import EFLRTable, EFLRItem
from dlis_writer.logical_record.eflr_types.equipment import EquipmentTable
from dlis_writer.logical_record.eflr_types.channel import ChannelTable
from dlis_writer.logical_record.eflr_types.parameter import ParameterTable
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute


logger = logging.getLogger(__name__)


class ToolItem(EFLRItem):
    """Model an object being part of Tool EFLR."""

    parent: "ToolTable"

    def __init__(self, name: str, **kwargs):
        """Initialise ToolObject.

        Args:
            name        :   Name of the ToolObject.
            **kwargs    :   Values of to be set as characteristics of the ToolObject Attributes.
        """

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.generic_name = Attribute('generic_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.parts = EFLRAttribute('parts', object_class=EquipmentTable, multivalued=True, parent_eflr=self)
        self.status = Attribute('status', converter=int, representation_code=RepC.STATUS, parent_eflr=self)
        self.channels = EFLRAttribute('channels', object_class=ChannelTable, multivalued=True, parent_eflr=self)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterTable, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class ToolTable(EFLRTable):
    """Model Tool EFLR."""

    set_type = 'TOOL'
    logical_record_type = EFLRType.STATIC
    object_type = ToolItem


ToolItem.parent_eflr_class = ToolTable
