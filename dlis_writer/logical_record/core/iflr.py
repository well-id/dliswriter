from dlis_writer.utils.enums import IFLRType
from dlis_writer.logical_record.core.logical_record import LogicalRecord


class IFLR(LogicalRecord):
    """Similar to EFLR object with is_eflr=False

    Methods docstrings are not added as they are the same with EFLR.
    """

    logical_record_type: IFLRType
    is_eflr = False

    def __init__(self):
        super().__init__()
