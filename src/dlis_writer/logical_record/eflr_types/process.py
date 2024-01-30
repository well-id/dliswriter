import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.logical_record.eflr_types.channel import ChannelSet
from dlis_writer.logical_record.eflr_types.computation import ComputationSet
from dlis_writer.logical_record.eflr_types.parameter import ParameterSet
from dlis_writer.utils.enums import EFLRType, PROPERTIES
from dlis_writer.logical_record.core.attribute import EFLRAttribute, TextAttribute, IdentAttribute


logger = logging.getLogger(__name__)


class ProcessItem(EFLRItem):
    """Model an object being part of Process EFLR."""

    parent: "ProcessSet"

    allowed_status = ('COMPLETE', 'ABORTED', 'IN-PROGRESS')  #: allowed values of the 'status' Attribute

    def __init__(self, name: str, parent: "ProcessSet", **kwargs: Any) -> None:
        """Initialise ProcessItem.

        Args:
            name        :   Name of the ProcessItem.
            parent      :   Parent ProcessSet of this ProcessItem.
            **kwargs    :   Values of to be set as characteristics of the ProcessItem Attributes.
        """

        self.description = TextAttribute('description')
        self.trademark_name = TextAttribute('trademark_name')
        self.version = TextAttribute('version')
        self.properties = IdentAttribute('properties', multivalued=True, converter=self._convert_property)
        self.status = IdentAttribute('status', converter=self.check_status)
        self.input_channels = EFLRAttribute('input_channels', object_class=ChannelSet, multivalued=True)
        self.output_channels = EFLRAttribute('output_channels', object_class=ChannelSet, multivalued=True)
        self.input_computations = EFLRAttribute('input_computations', object_class=ComputationSet, multivalued=True)
        self.output_computations = EFLRAttribute('output_computations', object_class=ComputationSet, multivalued=True)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterSet, multivalued=True)
        self.comments = TextAttribute('comments', multivalued=True)

        super().__init__(name, parent=parent, **kwargs)

    @classmethod
    def check_status(cls, status: str) -> str:
        if status not in cls.allowed_status:
            raise ValueError(f"'status' should be one of: {', '.join(cls.allowed_status)}; got {status}")
        return status

    @classmethod
    def _convert_property(cls, v: str) -> str:
        """Check that the provided property indicator is one of the accepted ones."""

        if not isinstance(v, str):
            raise TypeError(f"Expected a str, got {type(v)}: {v}")

        v_corrected = v.upper().replace(' ', '-').replace('_', '-')
        if v_corrected not in PROPERTIES:
            raise ValueError(f"{repr(v)} is not one of the allowed property indicators: "
                             f"{', '.join(PROPERTIES)}")

        return v_corrected


class ProcessSet(EFLRSet):
    """Model Process EFLR."""

    set_type = 'PROCESS'
    logical_record_type = EFLRType.STATIC
    item_type = ProcessItem


ProcessItem.parent_eflr_class = ProcessSet
