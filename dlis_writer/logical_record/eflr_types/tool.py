import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.equipment import Equipment
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


logger = logging.getLogger(__name__)


class Tool(EFLR):
    set_type = 'TOOL'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.description = self._create_attribute('description', representation_code=RepC.ASCII)
        self.trademark_name = self._create_attribute('trademark_name', representation_code=RepC.ASCII)
        self.generic_name = self._create_attribute('generic_name', representation_code=RepC.ASCII)
        self.parts = self._create_attribute('parts', multivalued=True, representation_code=RepC.OBNAME)
        self.status = self._create_attribute('status', converter=int, representation_code=RepC.STATUS)
        self.channels = self._create_attribute('channels', multivalued=True, representation_code=RepC.OBNAME)
        self.parameters = self._create_attribute('parameters', multivalued=True, representation_code=RepC.OBNAME)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'parts', Equipment)
        obj.add_dependent_objects_from_config(config, 'channels', Channel)
        obj.add_dependent_objects_from_config(config, 'parameters', Parameter)

        return obj

