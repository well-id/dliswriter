import numpy as np
from functools import lru_cache

from dlis_writer.utils.converters import get_ascii_bytes
from dlis_writer.logical_record.core.logical_record_base import LogicalRecordBase


class StorageUnitLabel(LogicalRecordBase):
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

    set_type = NotImplemented  # TODO

    def __init__(self,
                 storage_unit_sequence_number:int=1, # It indicates the order in which the current Storage Unit appears in a Storage Set.
                 storage_set_identifier:str='DEFAULT STORAGE SET', # ID of the storage set (eg. "Default Storage Set")
                 dlis_version='V1.00',
                 storage_unit_structure='RECORD',
                 max_record_length=8192):

        self.storage_unit_sequence_number = storage_unit_sequence_number
        self.dlis_version = dlis_version
        self.storage_unit_structure = storage_unit_structure # ONLY one value is allowed -> 'RECORD'
        self.max_record_length = max_record_length # http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_5
        self.storage_set_identifier = storage_set_identifier

    @lru_cache(maxsize=4096)
    def represent_as_bytes(self) -> np.ndarray:
        """Converts the arguments passed to __init__ to ASCII as per the RP66 V1 spec

        Returns:
            Bytes of complete Storage Unit Label
        """

        # Storage Unit Sequence Number
        _susn_as_bytes = get_ascii_bytes(self.storage_unit_sequence_number, 4)

        # DLIS Version
        _dlisv_as_bytes = get_ascii_bytes(self.dlis_version, 5, justify_left=True)

        # Storage Unit Structure
        _sus_as_bytes = get_ascii_bytes(self.storage_unit_structure, 6)

        # Maximum Record Length
        _mrl_as_bytes = get_ascii_bytes(self.max_record_length, 5)

        # Storage Set Identifier
        _ssi_as_bytes = get_ascii_bytes(self.storage_set_identifier, 60, justify_left=True)

        bts = _susn_as_bytes + _dlisv_as_bytes + _sus_as_bytes + _mrl_as_bytes + _ssi_as_bytes
        return np.frombuffer(bts, dtype=np.uint8)

    @property
    def size(self):
        raise RuntimeError(f"Size of {type(self)} is undefined")  # TODO: verify (probably never needed)
