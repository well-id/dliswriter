import re
from configparser import ConfigParser
import logging

from dlis_writer.logical_record.core.logical_record import LRMeta
from dlis_writer.logical_record.core.eflr.eflr_object import EFLRObject


logger = logging.getLogger(__name__)


class EFLRMeta(LRMeta):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj._instance_dict = {}
        return obj

    def clear_eflr_instance_dict(cls):
        if cls._instance_dict:
            logger.debug(f"Removing all defined instances of {cls.__name__}")
            cls._instance_dict.clear()

    def get_or_make_eflr(cls, set_name):
        if set_name in cls._instance_dict:
            return cls._instance_dict[set_name]

        return cls(set_name)

    def get_all_instances(cls):
        return list(cls._instance_dict.values())

    def make_object(cls, name, set_name=None, **kwargs) -> EFLRObject:
        eflr_instance = cls.get_or_make_eflr(set_name=set_name)

        return eflr_instance.make_object_in_this_set(name, **kwargs)

    def make_object_from_config(cls, config: ConfigParser, key=None, get_if_exists=False) -> EFLRObject:
        key = key or cls.__name__

        if key not in config.sections():
            raise RuntimeError(f"Section '{key}' not present in the config")

        name_key = "name"

        if name_key not in config[key].keys():
            raise RuntimeError(f"Required item '{name_key}' not present in the config section '{key}'")

        other_kwargs = {k: v for k, v in config[key].items() if k != name_key}

        obj = cls.make_object(config[key][name_key], **other_kwargs, get_if_exists=get_if_exists)

        for attr in obj.attributes.values():
            if hasattr(attr, 'finalise_from_config'):  # EFLRAttribute; cannot be imported here - circular import issue
                attr.finalise_from_config(config)

        return obj

    def make_all_objects_from_config(cls, config: ConfigParser, keys: list[str] = None, key_pattern: str = None, **kwargs):
        if not keys:
            if key_pattern is None:
                key_pattern = cls.__name__ + r"-\w+"
            key_pattern = re.compile(key_pattern)
            keys = [key for key in config.sections() if key_pattern.fullmatch(key)]

        return [cls.make_object_from_config(config, key=key, **kwargs) for key in keys]


