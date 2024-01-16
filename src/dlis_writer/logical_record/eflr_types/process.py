import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.logical_record.eflr_types.channel import ChannelSet
from dlis_writer.logical_record.eflr_types.computation import ComputationSet
from dlis_writer.logical_record.eflr_types.parameter import ParameterSet
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import EFLRAttribute, TextAttribute, IdentAttribute


logger = logging.getLogger(__name__)


class ProcessItem(EFLRItem):
    """Model an object being part of Process EFLR."""

    parent: "ProcessSet"

    allowed_status = ('COMPLETE', 'ABORTED', 'IN-PROGRESS')  #: allowed values of the 'status' Attribute

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise ProcessItem.

        Args:
            name        :   Name of the ProcessItem.
            **kwargs    :   Values of to be set as characteristics of the ProcessItem Attributes.
        """

        self.description = TextAttribute('description', parent_eflr=self)
        self.trademark_name = TextAttribute('trademark_name', parent_eflr=self)
        self.version = TextAttribute('version', parent_eflr=self)
        self.properties = IdentAttribute('properties', multivalued=True, parent_eflr=self)
        self.status = IdentAttribute('status', converter=self.check_status, parent_eflr=self)
        self.input_channels = EFLRAttribute(
            'input_channels', object_class=ChannelSet, multivalued=True, parent_eflr=self)
        self.output_channels = EFLRAttribute(
            'output_channels', object_class=ChannelSet, multivalued=True, parent_eflr=self)
        self.input_computations = EFLRAttribute(
            'input_computations', object_class=ComputationSet, multivalued=True, parent_eflr=self)
        self.output_computations = EFLRAttribute(
            'output_computations', object_class=ComputationSet, multivalued=True, parent_eflr=self)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterSet, multivalued=True, parent_eflr=self)
        self.comments = TextAttribute('comments', multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)

    @classmethod
    def check_status(cls, status: str) -> str:
        if status not in cls.allowed_status:
            raise ValueError(f"'status' should be one of: {', '.join(cls.allowed_status)}; got {status}")
        return status


class ProcessSet(EFLRSet):
    """Model Process EFLR."""

    set_type = 'PROCESS'
    logical_record_type = EFLRType.STATIC
    item_type = ProcessItem


ProcessItem.parent_eflr_class = ProcessSet
