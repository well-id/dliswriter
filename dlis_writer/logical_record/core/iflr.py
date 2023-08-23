from abc import ABC

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.iflr_eflr_base import IflrAndEflrBase


class IFLR(IflrAndEflrBase, ABC):
    """Similar to EFLR object with is_eflr=False

    Methods docstrings are not added as they are the same with EFLR.
    """

    is_eflr = False

    def __init__(self):
        super().__init__()

        self.iflr_type = None

    def _write_struct_for_lr_type(self):
        return write_struct(RepresentationCode.USHORT, self.iflr_type)
