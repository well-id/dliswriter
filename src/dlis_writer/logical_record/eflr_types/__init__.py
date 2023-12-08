from dlis_writer.logical_record.eflr_types.axis import AxisTable
from dlis_writer.logical_record.eflr_types.calibration import (CalibrationTable, CalibrationMeasurementTable,
                                                               CalibrationCoefficientTable)
from dlis_writer.logical_record.eflr_types.channel import ChannelTable
from dlis_writer.logical_record.eflr_types.computation import ComputationTable
from dlis_writer.logical_record.eflr_types.equipment import EquipmentTable
from dlis_writer.logical_record.eflr_types.frame import FrameTable
from dlis_writer.logical_record.eflr_types.group import GroupTable
from dlis_writer.logical_record.eflr_types.long_name import LongNameTable
from dlis_writer.logical_record.eflr_types.message import MessageTable, CommentTable
from dlis_writer.logical_record.eflr_types.no_format import NoFormatTable
from dlis_writer.logical_record.eflr_types.origin import OriginTable
from dlis_writer.logical_record.eflr_types.parameter import ParameterTable
from dlis_writer.logical_record.eflr_types.path import PathTable
from dlis_writer.logical_record.eflr_types.process import ProcessTable
from dlis_writer.logical_record.eflr_types.splice import SpliceTable
from dlis_writer.logical_record.eflr_types.tooltable import ToolTable
from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePointTable
from dlis_writer.logical_record.eflr_types.zone import ZoneTable

from dlis_writer.logical_record.eflr_types.file_header import FileHeaderTable


eflr_types = (
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
