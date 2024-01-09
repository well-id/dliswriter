import logging

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.logical_record.eflr_types.frame import FrameSet
from dlis_writer.logical_record.eflr_types.channel import ChannelSet
from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePointSet
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import EFLRAttribute, NumericAttribute


logger = logging.getLogger(__name__)


class PathItem(EFLRItem):
    """Model an object being part of Path EFLR."""

    parent: "PathSet"

    def __init__(self, name: str, **kwargs):
        """Initialise PathItem.

        Args:
            name        :   Name of the PathItem.
            **kwargs    :   Values of to be set as characteristics of the PathItem Attributes.
        """

        self.frame_type = EFLRAttribute('frame_type', object_class=FrameSet, parent_eflr=self)
        self.well_reference_point = EFLRAttribute(
            'well_reference_point', object_class=WellReferencePointSet, parent_eflr=self)
        self.value = EFLRAttribute('value', object_class=ChannelSet, multivalued=True, parent_eflr=self)
        self.borehole_depth = NumericAttribute('borehole_depth', parent_eflr=self)
        self.vertical_depth = NumericAttribute('vertical_depth', parent_eflr=self)
        self.radial_drift = NumericAttribute('radial_drift', parent_eflr=self)
        self.angular_drift = NumericAttribute('angular_drift', parent_eflr=self)
        self.time = NumericAttribute('time', parent_eflr=self)
        self.depth_offset = NumericAttribute('depth_offset', parent_eflr=self)
        self.measure_point_offset = NumericAttribute('measure_point_offset', parent_eflr=self)
        self.tool_zero_offset = NumericAttribute('tool_zero_offset', parent_eflr=self)

        super().__init__(name, **kwargs)


class PathSet(EFLRSet):
    """Model Path EFLR."""

    set_type = 'PATH'
    logical_record_type = EFLRType.FRAME
    item_type = PathItem


PathItem.parent_eflr_class = PathSet
