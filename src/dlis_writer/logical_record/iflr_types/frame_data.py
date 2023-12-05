import numpy as np
from typing import TYPE_CHECKING, Optional

from dlis_writer.logical_record.core.iflr import IFLR
from dlis_writer.utils.struct_writer import write_struct_uvari
from dlis_writer.utils.enums import IFLRType

if TYPE_CHECKING:
    from dlis_writer.logical_record.eflr_types.frame import FrameObject


class FrameData(IFLR):
    """Model FrameData - an Implicitly Formatted Logical Record meant for storing numerical data.

    Each FrameData record begins with a reference to the FrameObject that it belongs to.
    """

    logical_record_type = IFLRType.FDATA

    def __init__(self, frame: "FrameObject", frame_number: int, slots: np.ndarray,
                 origin_reference: Optional[int] = None):
        """Initialise a FrameData.

        Args:
            frame               :   The frame that the data belongs to.
            frame_number        :   Index of the frame, i.e. index (starting from 1) of the row of data.
            slots               :   Data belonging to the object. It should be a row of a structured numpy array
                                    with consecutive items corresponding to the channels in the frame.
            origin_reference    :   Origin reference for the object.
        """

        super().__init__()

        self._frame = frame
        self._frame_number = frame_number
        self._slots = slots

        self.origin_reference = origin_reference

    def _make_body_bytes(self) -> bytes:
        """Create bytes describing the body of the FrameData object.

        This includes: reference to the parent frame, placement of the FrameData object (the index), and the data.
        """

        body = self._frame.obname + write_struct_uvari(self._frame_number)

        for s in self._slots:
            body += s.byteswap().tobytes()

        return body
