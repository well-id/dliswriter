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
        self.status = self._create_attribute('status')
        self.channels = self._create_attribute('channels')
        self.parameters = self._create_attribute('parameters')

        self.set_attributes(**kwargs)

    @classmethod
    def from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().from_config(config, key=key)

        if (part_names := obj.parts.value) is not None:
            part_names_list = cls.convert_values(part_names)
            obj.parts.value = [Equipment.get_or_make_from_config(zn, config) for zn in part_names_list]
            
        if (channel_names := obj.channels.value) is not None:
            channel_names_list = cls.convert_values(channel_names)
            obj.channels.value = [Channel.get_or_make_from_config(zn, config) for zn in channel_names_list]
        
        if (param_names := obj.params.value) is not None:
            param_names_list = cls.convert_values(param_names)
            obj.params.value = [Parameter.get_or_make_from_config(zn, config) for zn in param_names_list]

        return obj

