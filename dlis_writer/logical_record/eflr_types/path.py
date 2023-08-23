from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Path(EFLR):
    set_type = 'PATH'
    logical_record_type = LogicalRecordType.FRAME

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.frame_type = None
        self.well_reference_point = None
        self.value = None
        self.borehole_depth = None
        self.vertical_depth = None
        self.radial_drift = None
        self.angular_drift = None
        self.time = None
        self.depth_offset = None
        self.measure_point_offset = None
        self.tool_zero_offset = None

        self.create_attributes()