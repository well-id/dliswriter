from .utils.core import EFLR


class Path(EFLR):
    
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'FRAME'
        self.set_type = 'PATH'

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