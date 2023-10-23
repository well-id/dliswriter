import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.frame import Frame
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePoint
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


logger = logging.getLogger(__name__)


class Path(EFLR):
    set_type = 'PATH'
    logical_record_type = LogicalRecordType.FRAME

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.frame_type = Attribute('frame_type', representation_code=RepC.OBNAME)
        self.well_reference_point = Attribute('well_reference_point', representation_code=RepC.OBNAME)
        self.value = Attribute('value', multivalued=True, representation_code=RepC.OBNAME)
        self.borehole_depth = Attribute('borehole_depth', converter=float)
        self.vertical_depth = Attribute('vertical_depth', converter=float)
        self.radial_drift = Attribute('radial_drift', converter=float)
        self.angular_drift = Attribute('angular_drift', converter=float)
        self.time = Attribute('time', converter=float)
        self.depth_offset = Attribute('depth_offset', converter=float)
        self.measure_point_offset = Attribute('measure_point_offset', converter=float)
        self.tool_zero_offset = Attribute('tool_zero_offset', converter=float)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'frame_type', Frame, single=True)
        obj.add_dependent_objects_from_config(config, 'well_reference_point', WellReferencePoint, single=True)
        obj.add_dependent_objects_from_config(config, 'value', Channel)

        return obj

