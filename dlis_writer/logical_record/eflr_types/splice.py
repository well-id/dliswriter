import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.logical_record.core.attribute import Attribute


logger = logging.getLogger(__name__)


class Splice(EFLR):
    set_type = 'SPLICE'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.output_channel = Attribute('output_channel', representation_code=RepC.OBNAME)
        self.input_channels = Attribute('input_channels', representation_code=RepC.OBNAME, multivalued=True)
        self.zones = Attribute('zones', representation_code=RepC.OBNAME, multivalued=True)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'input_channels', Channel)
        obj.add_dependent_objects_from_config(config, 'output_channel', Channel, single=True)
        obj.add_dependent_objects_from_config(config, 'zones', Zone)

        return obj
