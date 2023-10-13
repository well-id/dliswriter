from abc import ABC

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.iflr_eflr_base import IflrAndEflrBase


class IFLR(IflrAndEflrBase, ABC):
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

    @classmethod
    def from_config(cls, config):
        raise NotImplementedError("Initialising IFLR from a config is not supported")
