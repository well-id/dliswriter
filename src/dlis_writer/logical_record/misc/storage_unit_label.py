from configparser import ConfigParser
from typing_extensions import Self
from typing import Optional

from dlis_writer.utils.converters import get_ascii_bytes
from dlis_writer.logical_record.core.logical_record import LogicalRecordBytes


class StorageUnitLabel:
    """Model a Storage Unit Label - the first part of a DLIS file.

    Storage Unit Label is always 80 bytes long.
    
    Format:
        First 4 bytes:  Storage Unit Sequence Number
        Next 5 bytes:   DLIS version
        Next 6 bytes:   Storage Unit Structure
        Next 5 bytes:   Maximum Record Length
        Next 60 bytes:  Storage Set Identifier

    Although the StorageUnitLabel is not technically a LogicalRecord subclass, its interface has been adjusted so that
    it mocks the latter - for easier integration in the file writer.

    """

    storage_unit_structure = 'RECORD'   #: storage unit structure (this is the only allowed value)
    dlis_version = 'V1.00'              #: version of DLIS this implementation is for
    max_record_length_limit = 16384     #: maximal allowed length of a visible record

    def __init__(self, set_identifier: str, sequence_number: int = 1, max_record_length: int = 8192):
        """Initialise StorageUnitLabel.

        Args:
            sequence_number     :   Indicates the order in which the current Storage Unit appears in a Storage Set.
            set_identifier      :   ID of the storage set (e.g. "Default Storage Set").
            max_record_length   :   Maximum length of each visible record;
                                    see  # http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_5
        """

        super().__init__()

        self.sequence_number = sequence_number
        self.set_identifier = set_identifier
        self.max_record_length = max_record_length

        if max_record_length > self.max_record_length_limit:
            raise ValueError(f"Max record length cannot be larger than {self.max_record_length_limit}")

    def represent_as_bytes(self) -> LogicalRecordBytes:
        """Create bytes describing the storage unit label.

        Returns:
            Bytes of complete Storage Unit Label, wrapped in a LogicalRecordBytes object for consistency with
            Logical Records - other objects handled in the same loops as the SUL.
        """

        # Storage Unit Sequence Number
        _susn_as_bytes = get_ascii_bytes(str(self.sequence_number), 4)

        # DLIS Version
        _dlisv_as_bytes = get_ascii_bytes(self.dlis_version, 5, justify_left=True)

        # Storage Unit Structure
        _sus_as_bytes = get_ascii_bytes(self.storage_unit_structure, 6)

        # Maximum Record Length
        _mrl_as_bytes = get_ascii_bytes(str(self.max_record_length), 5)

        # Storage Set Identifier
        _ssi_as_bytes = get_ascii_bytes(self.set_identifier, 60, justify_left=True)

        bts = _susn_as_bytes + _dlisv_as_bytes + _sus_as_bytes + _mrl_as_bytes + _ssi_as_bytes

        return LogicalRecordBytes(bts, lr_type_struct=b'')
