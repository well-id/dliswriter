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

    @property
    def header_bytes(self) -> bytes:
        segment_length = len(self.body_bytes) + 4
        if segment_length % 2 != 0:
            segment_length += 1
            self.has_padding = True
        else:
            self.has_padding = False

        return write_struct(RepresentationCode.UNORM, segment_length) \
            + self.segment_attributes \
            + self._write_struct_for_lr_type()

    def _write_struct_for_lr_type(self):
        return write_struct(RepresentationCode.USHORT, self.iflr_type)
