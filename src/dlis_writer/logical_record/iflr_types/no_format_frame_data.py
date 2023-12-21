from dlis_writer.logical_record.core.iflr import IFLR
from dlis_writer.logical_record.core.logical_record.logical_record_bytes import LogicalRecordBytes
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

        if isinstance(self.data, (bytes, bytearray)):
            data_encoded = self.data
        else:
            data_encoded = self.data.encode('ascii')

        bts = self.no_format_object.obname + data_encoded

        # add padding if the length of the bts is less than minimum (12)
        padding_len = 12 - len(bts)
        if padding_len:
            bts += padding_len * LogicalRecordBytes.padding

        return bts

    @property
    def n_items(self) -> int:
        """Number of data items in this object."""
        return 1
