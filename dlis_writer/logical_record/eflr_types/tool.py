import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.equipment import Equipment
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.utils.enums import LogicalRecordType
from dlis_writer.logical_record.eflr_types._instance_register import InstanceRegisterMixin


logger = logging.getLogger(__name__)


class Tool(EFLR, InstanceRegisterMixin):
    set_type = 'TOOL'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        EFLR.__init__(self, object_name, set_name)
        InstanceRegisterMixin.__init__(self, object_name)

        self.description = self._create_attribute('description')
        self.trademark_name = self._create_attribute('trademark_name')
        self.generic_name = self._create_attribute('generic_name')
        self.parts = self._create_attribute('parts')
        self.status = self._create_attribute('status', converter=int)
        self.channels = self._create_attribute('channels')
        self.parameters = self._create_attribute('parameters')

        self.set_attributes(**kwargs)

    @classmethod
    def from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'parts', Equipment)
        obj.add_dependent_objects_from_config(config, 'channels', Channel)
        obj.add_dependent_objects_from_config(config, 'parameters', Parameter)

        return obj

