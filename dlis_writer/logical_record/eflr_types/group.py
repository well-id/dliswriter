import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core.eflr import EFLR
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute


logger = logging.getLogger(__name__)


class Group(EFLR):
    set_type = 'GROUP'
    logical_record_type = EFLRType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.description = Attribute('description', representation_code=RepC.ASCII)
        self.object_type = Attribute('object_type', representation_code=RepC.IDENT)
        self.object_list = EFLRAttribute('object_list', multivalued=True)
        self.group_list = EFLRAttribute('group_list', object_class=Group, multivalued=True)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        for attr in (obj.object_list, obj.group_list):
            attr.finalise_from_config(config)

        return obj

