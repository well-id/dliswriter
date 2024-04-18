from typing import Union

from dliswriter.logical_record.core.iflr import IFLR
from dliswriter.logical_record.core.logical_record.logical_record_bytes import LogicalRecordBytes
from dliswriter.utils.internal_enums import IFLRType
from dliswriter.logical_record.eflr_types.no_format import NoFormatItem


class NoFormatFrameData(IFLR):
    """Model a NoFormatFrameData - an Indirectly Formatted Logical Record with data in ASCII."""

    logical_record_type = IFLRType.NOFMT

    def __init__(self, no_format_object: NoFormatItem, data: Union[str, bytes, bytearray]) -> None:
        """Initialise NoFormatFrameData."""

        super().__init__()

        self.no_format_object = no_format_object
        self.data = data

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
