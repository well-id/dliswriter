from abc import abstractmethod
import numpy as np
from functools import cached_property
from configparser import ConfigParser
from typing_extensions import Self
import logging


logger = logging.getLogger(__name__)


class LogicalRecordBase:
    """Base for all logical record classes."""

    set_type: str = NotImplemented

    def __init__(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    @cached_property
    def key(self):
        return hash(type(self))

    @abstractmethod
    def represent_as_bytes(self) -> np.ndarray:
        pass

    @classmethod
    def from_config(cls, config: ConfigParser, key=None) -> Self:
        key = key or cls.__name__

        if key not in config.sections():
            raise RuntimeError(f"Section '{key}' not present in the config")
        
        name_key = "name"

        if name_key not in config[key].keys():
            raise RuntimeError(f"Required item '{name_key}' not present in the config section '{key}'")

        other_kwargs = {k: v for k, v in config[key].items() if k != name_key}

        obj = cls(config[key][name_key], **other_kwargs)

        return obj
