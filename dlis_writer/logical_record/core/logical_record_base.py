from abc import abstractmethod
import numpy as np
from functools import cached_property
from configparser import ConfigParser
from typing_extensions import Self
import logging

from dlis_writer.logical_record.core.segment_attributes import SegmentAttributes
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.common import write_struct


logger = logging.getLogger(__name__)


class LogicalRecordBytes:
    def __init__(self, bts, key, lr_type_struct=None):
        if isinstance(bts, (bytes, bytearray)):
            self._bts = np.frombuffer(bts, dtype=np.uint8)
        elif isinstance(bts, np.ndarray):
            self._bts = bts
        else:
            raise TypeError(f"Expected numpy.ndarray, bytes, or bytearray; got {type(bts)}")

        self.key = key
        self.lr_type_struct = lr_type_struct

        self.segment_attributes = SegmentAttributes()

    @property
    def bytes(self):
        return self._bts

    @property
    def size(self) -> int:
        return self._bts.size

    def split(self, segment_length: int, is_first: bool = False, is_last: bool = False) -> bytes:
        """Creates header bytes to be inserted into split position

        When a Logical Record Segment overflows a Visible Record, it must be split.
        A split operation involves:
            1. Changing the header of the first part of the split
            2. Adding a header to the second part of the split

        Args:
            is_first: Represents whether this is the first part of the split
            is_last: Represents whether this is the last part of the split
            segment_length: Length of the segment after split operation

        Returns:
            Header bytes to be inserted into split position

        """

        assert segment_length % 2 == 0, 'Split segment length is not an EVEN NUMBER'
        assert segment_length < self.size, 'Split segment length can not be larger than the whole segment'

        if self.lr_type_struct is None:
            raise RuntimeError("LR type struct is undefined")

        self.segment_attributes.mark_order(first=is_first, last=is_last)

        _attributes = self.segment_attributes.to_struct(no_padding=is_first)

        return write_struct(RepresentationCode.UNORM, segment_length) + _attributes + self.lr_type_struct

    def add_header_bytes(self):
        """Writes Logical Record Segment Header

        .._RP66 V1 Logical Record Segment Header:
            http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1

        """

        segment_length = self.size + 4
        if segment_length % 2 != 0:
            segment_length += 1
            self.segment_attributes.has_padding = True
        else:
            self.segment_attributes.has_padding = False

        header_bytes = write_struct(RepresentationCode.UNORM, segment_length) \
            + self.segment_attributes.to_struct()\
            + self.lr_type_struct

        new_bts = header_bytes + self._bts.tobytes()
        if self.segment_attributes.has_padding:
            new_bts += write_struct(RepresentationCode.USHORT, 1)

        self._bts = np.frombuffer(new_bts, dtype=np.uint8)


class LogicalRecord:
    """Base for all logical record classes."""

    set_type: str = NotImplemented

    def __init__(self, *args, **kwargs):
        pass

    @cached_property
    def key(self):
        return hash(type(self))

    def _make_lrb(self, bts, **kwargs):
        return LogicalRecordBytes(bts, key=self.key, **kwargs)

    @abstractmethod
    def represent_as_bytes(self) -> LogicalRecordBytes:
        pass

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        key = key or cls.__name__

        if key not in config.sections():
            raise RuntimeError(f"Section '{key}' not present in the config")
        
        name_key = "name"

        if name_key not in config[key].keys():
            raise RuntimeError(f"Required item '{name_key}' not present in the config section '{key}'")

        other_kwargs = {k: v for k, v in config[key].items() if k != name_key}

        obj = cls(config[key][name_key], **other_kwargs)

        return obj
