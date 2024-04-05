from dlis_writer.logical_record.eflr_types.axis import AxisSet, AxisItem
from dlis_writer.logical_record.eflr_types.calibration_measurement import (CalibrationMeasurementItem,
                                                                           CalibrationMeasurementSet)
from dlis_writer.logical_record.eflr_types.calibration_coefficient import (CalibrationCoefficientSet,
                                                                           CalibrationCoefficientItem)
from dlis_writer.logical_record.eflr_types.calibration import CalibrationSet, CalibrationItem
from dlis_writer.logical_record.eflr_types.channel import ChannelSet, ChannelItem
from dlis_writer.logical_record.eflr_types.comment import CommentSet, CommentItem
from dlis_writer.logical_record.eflr_types.computation import ComputationSet, ComputationItem
from dlis_writer.logical_record.eflr_types.equipment import EquipmentSet, EquipmentItem
from dlis_writer.logical_record.eflr_types.frame import FrameSet, FrameItem
from dlis_writer.logical_record.eflr_types.group import GroupSet, GroupItem
from dlis_writer.logical_record.eflr_types.long_name import LongNameSet, LongNameItem
from dlis_writer.logical_record.eflr_types.message import MessageSet, MessageItem
from dlis_writer.logical_record.eflr_types.no_format import NoFormatSet, NoFormatItem
from dlis_writer.logical_record.eflr_types.origin import OriginSet, OriginItem
from dlis_writer.logical_record.eflr_types.parameter import ParameterSet, ParameterItem
from dlis_writer.logical_record.eflr_types.path import PathSet, PathItem
from dlis_writer.logical_record.eflr_types.process import ProcessSet, ProcessItem
from dlis_writer.logical_record.eflr_types.splice import SpliceSet, SpliceItem
from dlis_writer.logical_record.eflr_types.tool import ToolSet, ToolItem
from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePointSet, WellReferencePointItem
from dlis_writer.logical_record.eflr_types.zone import ZoneSet, ZoneItem

from dlis_writer.logical_record.eflr_types.file_header import FileHeaderSet, FileHeaderItem


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
