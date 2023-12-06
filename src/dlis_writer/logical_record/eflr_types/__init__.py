from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.eflr_types.calibration import (Calibration, CalibrationMeasurement,
                                                               CalibrationCoefficient)
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.computation import Computation
from dlis_writer.logical_record.eflr_types.equipment import Equipment
from dlis_writer.logical_record.eflr_types.frame import Frame
from dlis_writer.logical_record.eflr_types.group import Group
from dlis_writer.logical_record.eflr_types.long_name import LongName
from dlis_writer.logical_record.eflr_types.message import Message, Comment
from dlis_writer.logical_record.eflr_types.no_format import NoFormat
from dlis_writer.logical_record.eflr_types.origin import Origin
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.logical_record.eflr_types.path import Path
from dlis_writer.logical_record.eflr_types.process import Process
from dlis_writer.logical_record.eflr_types.splice import Splice
from dlis_writer.logical_record.eflr_types.tool import Tool
from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePoint
from dlis_writer.logical_record.eflr_types.zone import Zone

from dlis_writer.logical_record.eflr_types.file_header import FileHeader


eflr_types = (
    Axis,
    Calibration,
    CalibrationMeasurement,
    CalibrationCoefficient,
    Channel,
    Computation,
    Equipment,
    Frame,
    Group,
    LongName,
    Message,
    Comment,
    NoFormat,
    Origin,
    Parameter,
    Path,
    Process,
    Splice,
    Tool,
    WellReferencePoint,
    Zone,
    FileHeader
)
