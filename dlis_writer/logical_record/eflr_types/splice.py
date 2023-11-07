import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.logical_record.core.attribute import EFLRAttribute, EFLRAttribute


logger = logging.getLogger(__name__)


class Splice(EFLR):
    set_type = 'SPLICE'
    logical_record_type = EFLRType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.output_channel = EFLRAttribute('output_channel', object_class=Channel)
        self.input_channels = EFLRAttribute('input_channels', object_class=Channel, multivalued=True)
        self.zones = EFLRAttribute('zones', object_class=Zone, multivalued=True)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        for attr in (obj.output_channel, obj.input_channels, obj.zones):
            attr.finalise_from_config(config)

        return obj
