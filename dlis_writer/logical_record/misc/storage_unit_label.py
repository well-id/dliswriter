from functools import cached_property

from dlis_writer.utils.converters import get_ascii_bytes
from dlis_writer.logical_record.core.logical_record import ConfigGenMixin
from dlis_writer.logical_record.core.logical_record_bytes import BasicLogicalRecordBytes


class StorageUnitLabel(ConfigGenMixin):
    """Represents  the Storage Unit Label in RP66 V1
    
    This is the first part of a logical file.
    
    Format:
        First 4 bytes are "Storage Unit Sequence Number"
        Next 5 bytes represents "DLIS version"
        Next 6 bytes: "Storage Unit Structure"
        Next 5 bytes: "Maximum Record Length"
        Next 60 bytes: "Storage Set Identifier"

    Quote:
        The first 80 bytes of the Visible Envelope consist of 
        ASCII characters and constitute a Storage Unit Label.
        Figure 2-7 defines the format of the SUL.

    .._RP66 V1 Storage Unit Label (SUL):
        http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_2     
    
    .._dlispy StorageUnitLabel:
        https://github.com/Teradata/dlispy/blob/b2d682dbfd8a6f7d0074351b603e22f97524fee6/dlispy/StorageUnitLabel.py#L9

    """

    storage_unit_structure = 'RECORD'  # the only allowed value
    dlis_version = 'V1.00'
    max_record_length_limit = 16384

    def __init__(self, set_identifier: str, sequence_number: int = 1, max_record_length: int = 8192):
        """Initialise StorageUnitLabel.

        Args:
            sequence_number     :   Indicates the order in which the current Storage Unit appears in a Storage Set.
            set_identifier      :   ID of the storage set (e.g. "Default Storage Set").
            max_record_length   :   Maximum length of each visible record;
                                    see  # http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_5
        """

        super().__init__()

        self.sequence_number = int(sequence_number)
        self.set_identifier = set_identifier
        self.max_record_length = max_record_length

        if max_record_length > self.max_record_length_limit:
            raise ValueError(f"Max record length cannot be larger than {self.max_record_length_limit}")

        self._bytes = None

    def represent_as_bytes(self) -> BasicLogicalRecordBytes:
        """Converts the arguments passed to __init__ to ASCII as per the RP66 V1 spec

        Returns:
            Bytes of complete Storage Unit Label
        """

        if self._bytes is None:

            # Storage Unit Sequence Number
            _susn_as_bytes = get_ascii_bytes(self.sequence_number, 4)

            # DLIS Version
            _dlisv_as_bytes = get_ascii_bytes(self.dlis_version, 5, justify_left=True)

            # Storage Unit Structure
            _sus_as_bytes = get_ascii_bytes(self.storage_unit_structure, 6)

            # Maximum Record Length
            _mrl_as_bytes = get_ascii_bytes(self.max_record_length, 5)

            # Storage Set Identifier
            _ssi_as_bytes = get_ascii_bytes(self.set_identifier, 60, justify_left=True)

            bts = _susn_as_bytes + _dlisv_as_bytes + _sus_as_bytes + _mrl_as_bytes + _ssi_as_bytes
            self._bytes = BasicLogicalRecordBytes(bts, self.key)
        return self._bytes

    @cached_property
    def key(self):
        return hash(type(self))
