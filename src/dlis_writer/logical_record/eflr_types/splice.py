import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.eflr_types.channel import ChannelSet
from dlis_writer.logical_record.eflr_types.zone import ZoneSet
from dlis_writer.logical_record.core.attribute import EFLRAttribute


logger = logging.getLogger(__name__)


class SpliceItem(EFLRItem):
    """Model an object being part of Splice EFLR."""

    parent: "SpliceSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise SpliceItem.

        Args:
            name        :   Name of the SpliceItem.
            **kwargs    :   Values of to be set as characteristics of the SpliceItem Attributes.
        """

        self.output_channel = EFLRAttribute('output_channel', object_class=ChannelSet)
        self.input_channels = EFLRAttribute('input_channels', object_class=ChannelSet, multivalued=True)
        self.zones = EFLRAttribute('zones', object_class=ZoneSet, multivalued=True)

        super().__init__(name, **kwargs)


class SpliceSet(EFLRSet):
    """Model Splice EFLR."""

    set_type = 'SPLICE'
    logical_record_type = EFLRType.STATIC
    item_type = SpliceItem


SpliceItem.parent_eflr_class = SpliceSet
