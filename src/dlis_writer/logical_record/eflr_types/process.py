import logging

from dlis_writer.logical_record.core.eflr import EFLRTable, EFLRItem
from dlis_writer.logical_record.eflr_types.channel import ChannelTable
from dlis_writer.logical_record.eflr_types.computation import ComputationTable
from dlis_writer.logical_record.eflr_types.parameter import ParameterTable
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute


logger = logging.getLogger(__name__)


class ProcessItem(EFLRItem):
    """Model an object being part of Process EFLR."""

    parent: "ProcessTable"

    allowed_status = ('COMPLETE', 'ABORTED', 'IN-PROGRESS')  #: allowed values of the 'status' Attribute

    def __init__(self, name: str, **kwargs):
        """Initialise ProcessItem.

        Args:
            name        :   Name of the ProcessItem.
            **kwargs    :   Values of to be set as characteristics of the ProcessItem Attributes.
        """

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.version = Attribute('version', representation_code=RepC.ASCII, parent_eflr=self)
        self.properties = Attribute('properties', representation_code=RepC.IDENT, multivalued=True, parent_eflr=self)
        self.status = Attribute('status', converter=self.check_status, representation_code=RepC.IDENT, parent_eflr=self)
        self.input_channels = EFLRAttribute(
            'input_channels', object_class=ChannelTable, multivalued=True, parent_eflr=self)
        self.output_channels = EFLRAttribute(
            'output_channels', object_class=ChannelTable, multivalued=True, parent_eflr=self)
        self.input_computations = EFLRAttribute(
            'input_computations', object_class=ComputationTable, multivalued=True, parent_eflr=self)
        self.output_computations = EFLRAttribute(
            'output_computations', object_class=ComputationTable, multivalued=True, parent_eflr=self)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterTable, multivalued=True, parent_eflr=self)
        self.comments = Attribute('comments', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)

    @classmethod
    def check_status(cls, status):
        if status not in cls.allowed_status:
            raise ValueError(f"'status' should be one of: {', '.join(cls.allowed_status)}; got {status}")
        return status


class ProcessTable(EFLRTable):
    """Model Process EFLR."""

    set_type = 'PROCESS'
    logical_record_type = EFLRType.STATIC
    item_type = ProcessItem


ProcessItem.parent_eflr_class = ProcessTable
