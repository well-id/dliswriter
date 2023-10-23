import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core.eflr import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


logger = logging.getLogger(__name__)


class Group(EFLR):
    set_type = 'GROUP'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.description = self._create_attribute('description', representation_code=RepC.ASCII)
        self.object_type = self._create_attribute('object_type', representation_code=RepC.IDENT)
        self.object_list = self._create_attribute('object_list', representation_code=RepC.OBNAME, multivalued=True)
        self.group_list = self._create_attribute('group_list', representation_code=RepC.OBNAME, multivalued=True)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        key = key or cls.__name__
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'group_list', Group)
        obj.add_dependent_objects_from_config(config, 'object_list')

        return obj

