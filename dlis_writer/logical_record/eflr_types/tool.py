import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.equipment import Equipment
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRListAttribute


logger = logging.getLogger(__name__)


class Tool(EFLR):
    set_type = 'TOOL'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.description = Attribute('description', representation_code=RepC.ASCII)
        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII)
        self.generic_name = Attribute('generic_name', representation_code=RepC.ASCII)
        self.parts = EFLRListAttribute('parts', object_class=Equipment)
        self.status = Attribute('status', converter=int, representation_code=RepC.STATUS)
        self.channels = EFLRListAttribute('channels', object_class=Channel)
        self.parameters = EFLRListAttribute('parameters', object_class=Parameter)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        for attr in (obj.parts, obj.channels, obj.parameters):
            attr.finalise_from_config(config)

        return obj

