from abc import ABC

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.iflr_eflr_base import IflrAndEflrBase


def make_iflr_type_struct(iflr_type):
    return write_struct(RepresentationCode.USHORT, iflr_type)


class IFLR(IflrAndEflrBase, ABC):
    """Similar to EFLR object with is_eflr=False

    Methods docstrings are not added as they are the same with EFLR.
    """

    is_eflr = False
    iflr_type = NotImplemented
    iflr_type_struct = NotImplemented

    def __init__(self):
        super().__init__()

    def _write_struct_for_lr_type(self):
        return self.iflr_type_struct
