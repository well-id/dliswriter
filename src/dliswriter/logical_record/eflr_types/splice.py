import logging
from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.utils.internal_enums import EFLRType
from dliswriter.logical_record.eflr_types.channel import ChannelSet
from dliswriter.logical_record.eflr_types.zone import ZoneSet
from dliswriter.logical_record.core.attribute import EFLRAttribute


logger = logging.getLogger(__name__)


class SpliceItem(EFLRItem):
    """Model an object being part of Splice EFLR."""

    parent: "SpliceSet"

    def __init__(self, name: str, parent: "SpliceSet", **kwargs: Any) -> None:
        """Initialise SpliceItem.

        Args:
            name        :   Name of the SpliceItem.
            parent      :   Parent SpliceSet of this SpliceItem.
            **kwargs    :   Values of to be set as characteristics of the SpliceItem Attributes.
        """

        self.output_channel = EFLRAttribute('output_channel', object_class=ChannelSet)
        self.input_channels = EFLRAttribute('input_channels', object_class=ChannelSet, multivalued=True)
        self.zones = EFLRAttribute('zones', object_class=ZoneSet, multivalued=True)

        super().__init__(name, parent=parent, **kwargs)

    def _run_checks_and_set_defaults(self) -> None:
        """Check that the number of input channels and zones in the splice is the same."""

        if self.input_channels.value is not None and self.zones.value is not None:
            if (nc := self.input_channels.count) != (nz := self.zones.count):
                raise RuntimeError("A Splice must have the same number of input channels and zones if both are "
                                   f"defined; got {nc} channels and {nz} zones in {self}")


class SpliceSet(EFLRSet):
    """Model Splice EFLR."""

    set_type = 'SPLICE'
    logical_record_type = EFLRType.STATIC
    item_type = SpliceItem


SpliceItem.parent_eflr_class = SpliceSet
