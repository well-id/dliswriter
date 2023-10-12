from configparser import ConfigParser
from typing_extensions import Self
import logging

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType
from dlis_writer.logical_record.eflr_types import Channel


logger = logging.getLogger(__name__)


class Frame(EFLR):
    set_type = 'FRAME'
    logical_record_type = LogicalRecordType.FRAME
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, object_name: str, set_name: str = None, **kwargs):

        super().__init__(object_name, set_name)

        self.description = self._create_attribute('description')
        self.channels = self._create_attribute('channels')
        self.index_type = self._create_attribute('index_type')
        self.direction = self._create_attribute('direction')
        self.spacing = self._create_attribute('spacing', converter=float)
        self.encrypted = self._create_attribute('encrypted', converter=bool)
        self.index_min = self._create_attribute('index_min', converter=int)
        self.index_max = self._create_attribute('index_max', converter=int)

        self.set_attributes(**kwargs)

    @classmethod
    def from_config(cls, config: ConfigParser, key=None, add_channels=True) -> Self:
        obj: Self = super().from_config(config)

        channel_names = obj.channels.value
        if add_channels and not channel_names:
            logger.warning(f"No channels defined for frame {obj}")
        if not add_channels and channel_names:
            logger.info("Removing channel names added from config")
            obj.channels.value = None
        if channel_names and add_channels:
            logger.info(f"Adding channels for {obj}")
            channel_names_list = channel_names.rstrip(' ').rstrip(', ').split(', ')
            obj.channels.value = Channel.all_from_config(config, keys=channel_names_list)

        return obj

    def setup_channels_params_from_data(self, data):
        if not self.channels.value:
            raise RuntimeError(f"No channels defined for {self}")

        for channel in self.channels.value:
            channel.set_dimension_and_repr_code_from_data(data)


