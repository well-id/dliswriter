from configparser import ConfigParser
from typing_extensions import Self
import logging
import numpy as np

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types import Channel
from dlis_writer.logical_record.core.attribute import Attribute, EFLRListAttribute


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

        self.description = Attribute('description', representation_code=RepC.ASCII)
        self.channels = EFLRListAttribute('channels', object_class=Channel)
        self.index_type = Attribute('index_type', converter=self.parse_index_type, representation_code=RepC.IDENT)
        self.direction = Attribute('direction', representation_code=RepC.IDENT)
        self.spacing = Attribute('spacing', converter=float)
        self.encrypted = Attribute('encrypted', converter=bool, representation_code=RepC.USHORT)
        self.index_min = Attribute('index_min', converter=float)
        self.index_max = Attribute('index_max', converter=float)

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

        obj.channels.finalise_from_config(config)

        return obj

    def setup_from_data(self, data):
        if not self.channels.value:
            raise RuntimeError(f"No channels defined for {self}")

        for channel in self.channels.value:
            channel.set_dimension_and_repr_code_from_data(data)

        self._setup_frame_params_from_data(data)

    def _setup_frame_params_from_data(self, data):
        def assign_if_none(attr, value, key='value'):
            if getattr(attr, key) is None and value is not None:
                setattr(attr, key, value)

        index_channel: Channel = self.channels.value[0]
        index_data = data[index_channel.dataset_name]
        unit = index_channel.units.value
        repr_code = index_channel.representation_code.value
        spacing = np.median(np.diff(index_data))

        assign_if_none(self.index_min, index_data.min())
        assign_if_none(self.index_max, index_data.max())
        assign_if_none(self.spacing, spacing)
        assign_if_none(self.direction, 'INCREASING' if spacing > 0 else 'DECREASING')

        for attr in (self.index_min, self.index_max, self.spacing):
            assign_if_none(attr, key='units', value=unit)
            assign_if_none(attr, key='representation_code', value=repr_code)

