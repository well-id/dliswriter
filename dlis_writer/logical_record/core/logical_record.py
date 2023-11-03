from abc import abstractmethod
from functools import cached_property
from configparser import ConfigParser
from typing_extensions import Self
import logging

from dlis_writer.logical_record.core.logical_record_bytes import LogicalRecordBytes



logger = logging.getLogger(__name__)


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
