from configparser import ConfigParser
from typing_extensions import Self
import logging
from numbers import Number
import numpy as np

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.channel import Channel, ChannelObject
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute, NumericAttribute


logger = logging.getLogger(__name__)


class FrameObject(EFLRObject):
    frame_index_types = (
        'ANGULAR-DRIFT',
        'BOREHOLE-DEPTH',
        'NON-STANDARD',
        'RADIAL-DRIFT',
        'VERTICAL-DEPTH'
    )

    def __init__(self, name: str, parent, **kwargs):

        self.description = Attribute('description', representation_code=RepC.ASCII)
        self.channels = EFLRAttribute('channels', object_class=Channel, multivalued=True)
        self.index_type = Attribute('index_type', converter=self.parse_index_type, representation_code=RepC.IDENT)
        self.direction = Attribute('direction', representation_code=RepC.IDENT)
        self.spacing = NumericAttribute('spacing')
        self.encrypted = NumericAttribute(
            'encrypted', converter=self.convert_encrypted, representation_code=RepC.USHORT)
        self.index_min = NumericAttribute('index_min')
        self.index_max = NumericAttribute('index_max')

        super().__init__(name, parent, **kwargs)

    @classmethod
    def parse_index_type(cls, value):
        if value not in cls.frame_index_types:
            logger.warning(f"Frame index type should be one of the following: "
                           f"'{', '.join(cls.frame_index_types)}'; got '{value}'")
        return value

    @staticmethod
    def convert_encrypted(value):
        if isinstance(value, str):
            if value.lower() in ('1', 'true', 't', 'yes', 'y'):
                return 1
            elif value.lower() in ('0', 'false', 'f', 'no', 'n'):
                return 0
            else:
                raise ValueError(f"Couldn't evaluate the boolean meaning of '{value}'")
        if isinstance(value, Number):
            return int(bool(value))
        if isinstance(value, bool):
            return int(value)
        else:
            raise TypeError(f"Cannot convert {type(value)} object ({value}) to integer")

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

        index_channel: ChannelObject = self.channels.value[0]
        index_data = data[index_channel.dataset_name]
        unit = index_channel.units.value
        repr_code = index_channel.representation_code.value or RepC.FDOUBL
        spacing = np.median(np.diff(index_data))

        assign_if_none(index_channel.representation_code, repr_code)
        assign_if_none(self.index_min, index_data.min())
        assign_if_none(self.index_max, index_data.max())
        assign_if_none(self.spacing, spacing)
        assign_if_none(self.direction, 'INCREASING' if spacing > 0 else 'DECREASING')

        for attr in (self.index_min, self.index_max, self.spacing):
            assign_if_none(attr, key='units', value=unit)
            if attr.assigned_representation_code is None:
                attr.representation_code = repr_code


class Frame(EFLR):
    set_type = 'FRAME'
    logical_record_type = EFLRType.FRAME
    object_type = FrameObject

    def make_object_from_config(self, config: ConfigParser, key=None) -> FrameObject:
        obj: FrameObject = super().make_object_from_config(config, key=key)

        obj.channels.finalise_from_config(config)

        return obj

