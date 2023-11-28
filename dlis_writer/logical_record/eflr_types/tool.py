import logging

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.logical_record.eflr_types.equipment import Equipment
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute


logger = logging.getLogger(__name__)


class ToolObject(EFLRObject):
    """Model an object being part of Tool EFLR."""

    def __init__(self, name: str, parent: "Tool", **kwargs):
        """Initialise ToolObject.

        Args:
            name        :   Name of the ToolObject.
            parent      :   Tool EFLR instance this ToolObject belongs to.
            **kwargs    :   Values of to be set as characteristics of the ToolObject Attributes.
        """

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.generic_name = Attribute('generic_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.parts = EFLRAttribute('parts', object_class=Equipment, multivalued=True, parent_eflr=self)
        self.status = Attribute('status', converter=int, representation_code=RepC.STATUS, parent_eflr=self)
        self.channels = EFLRAttribute('channels', object_class=Channel, multivalued=True, parent_eflr=self)
        self.parameters = EFLRAttribute('parameters', object_class=Parameter, multivalued=True, parent_eflr=self)

        super().__init__(name, parent, **kwargs)


class Tool(EFLR):
    """Model Tool EFLR."""

    set_type = 'TOOL'
    logical_record_type = EFLRType.STATIC
    object_type = ToolObject
