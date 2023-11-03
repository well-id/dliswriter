from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.logical_record import LogicalRecord


class IFLR(LogicalRecord):
    """Similar to EFLR object with is_eflr=False

    Methods docstrings are not added as they are the same with EFLR.
    """

    logical_record_type: int
    is_eflr = False

    def __init__(self):
        super().__init__()

    @classmethod
    def make_lr_type_struct(cls, iflr_type):
        return write_struct(RepresentationCode.USHORT, iflr_type)
