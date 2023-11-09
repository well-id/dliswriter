import logging

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.logical_record.core.attribute import EFLRAttribute


logger = logging.getLogger(__name__)


class SpliceObject(EFLRObject):

    def __init__(self, name: str, parent: "Splice", **kwargs):

        self.output_channel = EFLRAttribute('output_channel', object_class=Channel)
        self.input_channels = EFLRAttribute('input_channels', object_class=Channel, multivalued=True)
        self.zones = EFLRAttribute('zones', object_class=Zone, multivalued=True)

        super().__init__(name, parent, **kwargs)


class Splice(EFLR):
    set_type = 'SPLICE'
    logical_record_type = EFLRType.STATIC
    object_type = SpliceObject
