import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.frame import Frame
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePoint
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute, EFLRAttribute, NumericAttribute


logger = logging.getLogger(__name__)


class Path(EFLR):
    set_type = 'PATH'
    logical_record_type = LogicalRecordType.FRAME

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.frame_type = EFLRAttribute('frame_type', object_class=Frame)
        self.well_reference_point = EFLRAttribute('well_reference_point', object_class=WellReferencePoint)
        self.value = EFLRAttribute('value', object_class=Channel, multivalued=True)
        self.borehole_depth = NumericAttribute('borehole_depth')
        self.vertical_depth = NumericAttribute('vertical_depth')
        self.radial_drift = NumericAttribute('radial_drift')
        self.angular_drift = NumericAttribute('angular_drift')
        self.time = NumericAttribute('time')
        self.depth_offset = NumericAttribute('depth_offset')
        self.measure_point_offset = NumericAttribute('measure_point_offset')
        self.tool_zero_offset = NumericAttribute('tool_zero_offset')

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        for attr in (obj.frame_type, obj.well_reference_point, obj.value):
            attr.finalise_from_config(config)

        return obj

