from dliswriter.logical_record.eflr_types.axis import AxisSet, AxisItem
from dliswriter.logical_record.eflr_types.calibration_measurement import (CalibrationMeasurementItem,
                                                                          CalibrationMeasurementSet)
from dliswriter.logical_record.eflr_types.calibration_coefficient import (CalibrationCoefficientSet,
                                                                          CalibrationCoefficientItem)
from dliswriter.logical_record.eflr_types.calibration import CalibrationSet, CalibrationItem
from dliswriter.logical_record.eflr_types.channel import ChannelSet, ChannelItem
from dliswriter.logical_record.eflr_types.comment import CommentSet, CommentItem
from dliswriter.logical_record.eflr_types.computation import ComputationSet, ComputationItem
from dliswriter.logical_record.eflr_types.equipment import EquipmentSet, EquipmentItem
from dliswriter.logical_record.eflr_types.frame import FrameSet, FrameItem
from dliswriter.logical_record.eflr_types.group import GroupSet, GroupItem
from dliswriter.logical_record.eflr_types.long_name import LongNameSet, LongNameItem
from dliswriter.logical_record.eflr_types.message import MessageSet, MessageItem
from dliswriter.logical_record.eflr_types.no_format import NoFormatSet, NoFormatItem
from dliswriter.logical_record.eflr_types.origin import OriginSet, OriginItem
from dliswriter.logical_record.eflr_types.parameter import ParameterSet, ParameterItem
from dliswriter.logical_record.eflr_types.path import PathSet, PathItem
from dliswriter.logical_record.eflr_types.process import ProcessSet, ProcessItem
from dliswriter.logical_record.eflr_types.splice import SpliceSet, SpliceItem
from dliswriter.logical_record.eflr_types.tool import ToolSet, ToolItem
from dliswriter.logical_record.eflr_types.well_reference_point import WellReferencePointSet, WellReferencePointItem
from dliswriter.logical_record.eflr_types.zone import ZoneSet, ZoneItem

from dliswriter.logical_record.eflr_types.file_header import FileHeaderSet, FileHeaderItem


eflr_sets = (
    AxisSet,
    CalibrationSet,
    CalibrationMeasurementSet,
    CalibrationCoefficientSet,
    ChannelSet,
    ComputationSet,
    EquipmentSet,
    FrameSet,
    GroupSet,
    LongNameSet,
    MessageSet,
    CommentSet,
    NoFormatSet,
    OriginSet,
    ParameterSet,
    PathSet,
    ProcessSet,
    SpliceSet,
    ToolSet,
    WellReferencePointSet,
    ZoneSet,
    FileHeaderSet
)


eflr_items = (
    AxisItem,
    CalibrationItem,
    CalibrationMeasurementItem,
    CalibrationCoefficientItem,
    ChannelItem,
    ComputationItem,
    EquipmentItem,
    FrameItem,
    GroupItem,
    LongNameItem,
    MessageItem,
    CommentItem,
    NoFormatItem,
    OriginItem,
    ParameterItem,
    PathItem,
    ProcessItem,
    SpliceItem,
    ToolItem,
    WellReferencePointItem,
    ZoneItem,
    FileHeaderItem
)
