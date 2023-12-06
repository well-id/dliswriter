from dlis_writer.logical_record.core.iflr import IFLR
from dlis_writer.utils.enums import IFLRType


class NoFormatFrameData(IFLR):
    """Model a NoFormatFrameData - an Indirectly Formatted Logical Record with data in ASCII."""

    logical_record_type = IFLRType.NOFMT

    def __init__(self):
        """Initialise NoFormatFrameData."""

        super().__init__()

        self.no_format_object = None
        self.data = None

    def _make_body_bytes(self) -> bytes:
        """Create bytes representing the body of the object."""

        return self.no_format_object.obname + self.data.encode('ascii')
