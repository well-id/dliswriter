from abc import abstractmethod
from configparser import ConfigParser
from typing_extensions import Self
import logging
from typing import Union

from dlis_writer.logical_record.core.logical_record_bytes import LogicalRecordBytes
from dlis_writer.utils.enums import RepresentationCode, EFLRType, IFLRType
from dlis_writer.utils.common import write_struct


logger = logging.getLogger(__name__)


class ConfigGenMixin:
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


class LRMeta(type):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj._lr_type_struct = None
        return obj

    @property
    def lr_type_struct(cls):
        if not cls._lr_type_struct:
            cls._lr_type_struct = write_struct(RepresentationCode.USHORT, cls.logical_record_type.value)
        return cls._lr_type_struct


class LogicalRecord(metaclass=LRMeta):
    """Base for all logical record classes."""

    set_type: str = NotImplemented
    is_eflr = NotImplemented
    logical_record_type: Union[EFLRType, IFLRType] = NotImplemented

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def make_body_bytes(self) -> bytes:
        pass

    def represent_as_bytes(self) -> LogicalRecordBytes:
        """Writes bytes of the entire Logical Record Segment that is an EFLR object"""

        return LogicalRecordBytes(
            self.make_body_bytes(),
            lr_type_struct=self.__class__.lr_type_struct,
            is_eflr=self.is_eflr
        )
