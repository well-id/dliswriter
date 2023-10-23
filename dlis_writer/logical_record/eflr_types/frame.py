from configparser import ConfigParser
from typing_extensions import Self
import logging

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types import Channel


logger = logging.getLogger(__name__)


class Frame(EFLR):
    set_type = 'FRAME'
    logical_record_type = LogicalRecordType.FRAME
    frame_index_types = (
        'ANGULAR-DRIFT',
        'BOREHOLE-DEPTH',
        'NON-STANDARD',
        'RADIAL-DRIFT',
        'VERTICAL-DEPTH'
    )

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.description = self._create_attribute('description', representation_code=RepC.ASCII)
        self.channels = self._create_attribute('channels', multivalued=True, representation_code=RepC.OBNAME)
        self.index_type = self._create_attribute(
            'index_type', converter=self.parse_index_type, representation_code=RepC.IDENT)
        self.direction = self._create_attribute('direction', representation_code=RepC.IDENT)
        self.spacing = self._create_attribute('spacing', converter=float)
        self.encrypted = self._create_attribute('encrypted', converter=bool, representation_code=RepC.USHORT)
        self.index_min = self._create_attribute('index_min', converter=int)
        self.index_max = self._create_attribute('index_max', converter=int)

        self.set_attributes(**kwargs)

    @staticmethod
    def parse_index_type(value):
        if value not in Frame.frame_index_types:
            logger.warning(f"Frame index type should be one of the following: "
                           f"'{', '.join(Frame.frame_index_types)}'; got '{value}'")
        return value

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config)

        if not (channel_names := obj.channels.value):
            logger.warning(f"No channels defined for frame {obj}")
            if channel_names is not None:  # e.g. empty string
                obj.channels.value = None

        else:
            logger.info(f"Adding channels for {obj}")
            obj.add_dependent_objects_from_config(config, 'channels', Channel)

        return obj

    def setup_from_data(self, data):
        if not self.channels.value:
            raise RuntimeError(f"No channels defined for {self}")

        for channel in self.channels.value:
            channel.set_dimension_and_repr_code_from_data(data)

        self._setup_index_max_and_min_from_data(data)

    def _setup_index_max_and_min_from_data(self, data):
        def assign_if_none(attr, value, key='value'):
            if getattr(attr, key) is None:
                setattr(attr, key, value)

        index_channel = self.channels.value[0].dataset_name
        assign_if_none(self.spacing, RepC.FDOUBL, 'representation_code')
        assign_if_none(self.index_min, data[index_channel].min())
        assign_if_none(self.index_max, data[index_channel].max())
        assign_if_none(self.index_min, RepC.FDOUBL, 'representation_code')
        assign_if_none(self.index_max, RepC.FDOUBL, 'representation_code')



