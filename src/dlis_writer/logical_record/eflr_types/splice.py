import logging

from dlis_writer.logical_record.core.eflr import EFLRTable, EFLRItem
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.eflr_types.channel import ChannelTable
from dlis_writer.logical_record.eflr_types.zone import ZoneTable
from dlis_writer.logical_record.core.attribute import EFLRAttribute


logger = logging.getLogger(__name__)


class SpliceItem(EFLRItem):
    """Model an object being part of Splice EFLR."""

    parent: "SpliceTable"

    def __init__(self, name: str, **kwargs):
        """Initialise SpliceObject.

        Args:
            name        :   Name of the SpliceObject.
            **kwargs    :   Values of to be set as characteristics of the SpliceObject Attributes.
        """

        self.output_channel = EFLRAttribute('output_channel', object_class=ChannelTable, parent_eflr=self)
        self.input_channels = EFLRAttribute('input_channels', object_class=ChannelTable, multivalued=True, parent_eflr=self)
        self.zones = EFLRAttribute('zones', object_class=ZoneTable, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class SpliceTable(EFLRTable):
    """Model Splice EFLR."""

    set_type = 'SPLICE'
    logical_record_type = EFLRType.STATIC
    object_type = SpliceItem


SpliceItem.parent_eflr_class = SpliceTable
