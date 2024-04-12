import logging
from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.logical_record.eflr_types.frame import FrameSet
from dliswriter.logical_record.eflr_types.channel import ChannelSet
from dliswriter.logical_record.eflr_types.well_reference_point import WellReferencePointSet
from dliswriter.utils.internal_enums import EFLRType
from dliswriter.logical_record.core.attribute import EFLRAttribute, NumericAttribute


logger = logging.getLogger(__name__)


class PathItem(EFLRItem):
    """Model an object being part of Path EFLR."""

    parent: "PathSet"

    def __init__(self, name: str, parent: "PathSet", **kwargs: Any) -> None:
        """Initialise PathItem.

        Args:
            name        :   Name of the PathItem.
            parent      :   Parent PathSet of this PathItem.
            **kwargs    :   Values of to be set as characteristics of the PathItem Attributes.
        """

        self.frame_type = EFLRAttribute('frame_type', object_class=FrameSet)
        self.well_reference_point = EFLRAttribute('well_reference_point', object_class=WellReferencePointSet)
        self.value = EFLRAttribute('value', object_class=ChannelSet, multivalued=True)
        self.borehole_depth = NumericAttribute('borehole_depth')
        self.vertical_depth = NumericAttribute('vertical_depth')
        self.radial_drift = NumericAttribute('radial_drift')
        self.angular_drift = NumericAttribute('angular_drift')
        self.time = NumericAttribute('time')
        self.depth_offset = NumericAttribute('depth_offset')
        self.measure_point_offset = NumericAttribute('measure_point_offset')
        self.tool_zero_offset = NumericAttribute('tool_zero_offset')

        super().__init__(name, parent=parent, **kwargs)


class PathSet(EFLRSet):
    """Model Path EFLR."""

    set_type = 'PATH'
    logical_record_type = EFLRType.FRAME
    item_type = PathItem


PathItem.parent_eflr_class = PathSet
