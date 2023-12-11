from dlis_writer.logical_record.eflr_types.axis import AxisTable, AxisItem
from dlis_writer.logical_record.eflr_types.calibration import (CalibrationTable, CalibrationMeasurementTable,
                                                               CalibrationCoefficientTable, CalibrationItem, 
                                                               CalibrationMeasurementItem, CalibrationCoefficientItem)
from dlis_writer.logical_record.eflr_types.channel import ChannelTable, ChannelItem
from dlis_writer.logical_record.eflr_types.computation import ComputationTable, ComputationItem
from dlis_writer.logical_record.eflr_types.equipment import EquipmentTable, EquipmentItem
from dlis_writer.logical_record.eflr_types.frame import FrameTable, FrameItem
from dlis_writer.logical_record.eflr_types.group import GroupTable, GroupItem
from dlis_writer.logical_record.eflr_types.long_name import LongNameTable, LongNameItem
from dlis_writer.logical_record.eflr_types.message import MessageTable, CommentTable, MessageItem, CommentItem
from dlis_writer.logical_record.eflr_types.no_format import NoFormatTable, NoFormatItem
from dlis_writer.logical_record.eflr_types.origin import OriginTable, OriginItem
from dlis_writer.logical_record.eflr_types.parameter import ParameterTable, ParameterItem
from dlis_writer.logical_record.eflr_types.path import PathTable, PathItem
from dlis_writer.logical_record.eflr_types.process import ProcessTable, ProcessItem
from dlis_writer.logical_record.eflr_types.splice import SpliceTable, SpliceItem
from dlis_writer.logical_record.eflr_types.tool import ToolTable, ToolItem
from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePointTable, WellReferencePointItem
from dlis_writer.logical_record.eflr_types.zone import ZoneTable, ZoneItem

from dlis_writer.logical_record.eflr_types.file_header import FileHeaderTable, FileHeaderItem


eflr_tables = (
    AxisTable,
    CalibrationTable,
    CalibrationMeasurementTable,
    CalibrationCoefficientTable,
    ChannelTable,
    ComputationTable,
    EquipmentTable,
    FrameTable,
    GroupTable,
    LongNameTable,
    MessageTable,
    CommentTable,
    NoFormatTable,
    OriginTable,
    ParameterTable,
    PathTable,
    ProcessTable,
    SpliceTable,
    ToolTable,
    WellReferencePointTable,
    ZoneTable,
    FileHeaderTable
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
