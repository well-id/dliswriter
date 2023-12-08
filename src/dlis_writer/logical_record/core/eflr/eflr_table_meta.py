import re
from configparser import ConfigParser
import logging
from typing import TYPE_CHECKING, Optional, Union
from typing_extensions import Self

from dlis_writer.logical_record.core.logical_record import LRMeta

if TYPE_CHECKING:
    from dlis_writer.logical_record.core.eflr.eflr_table import EFLRTable


logger = logging.getLogger(__name__)


class EFLRTableMeta(LRMeta):
    """Define a metaclass for EFLR - Explicitly Formatted Logical Record.

    The main motivation for defining this metaclass is to be able to use an instance dictionary (see _instance_dict
    in __new__), which is separate for each subclass of EFLR.

    In addition, this metaclass implements several class methods of EFLR, mostly related to creating EFLR and EFLRObject
    instances, e.g. from a config object.
    """

    _instance_dict: dict[Union[str, None], "EFLRTable"]
    object_type: type
    eflr_name: str
    eflr_name_pattern = re.compile(r'(?P<name>\w+)Table')

    def __new__(cls, *args, **kwargs) -> "EFLRTableMeta":
        """Create a new EFLR class (instance of EFLRMeta).

        All positional and keyword arguments are passed to the super-metaclass: LRMeta.
        """

        obj = super().__new__(cls, *args, **kwargs)
        obj._instance_dict = {}
        obj.eflr_name = cls.eflr_name_pattern.fullmatch(obj.__name__).group('name')
        return obj

    def clear_eflr_instance_dict(cls):
        """Remove all instances of the EFLR (sub)class from the internal dictionary."""

        if cls._instance_dict:
            logger.debug(f"Removing all defined instances of {cls.__name__}")
            cls._instance_dict.clear()

    def get_or_make_eflr(cls, set_name: Optional[str] = None) -> "EFLRTable":
        """Retrieve an EFLR instance with given set name from the internal dict - if exists. Otherwise, create one."""

        if set_name in cls._instance_dict:
            return cls._instance_dict[set_name]

        return cls(set_name)

    def get_all_instances(cls) -> list["EFLRTable"]:
        """Return a list of all EFLR (subclass) instances which are stored in the internal dictionary."""

        return list(cls._instance_dict.values())

    def make_object_from_config(cls, config: ConfigParser, key: Optional[str] = None, get_if_exists: bool = False,
                                set_name: Optional[str] = None) -> "Self.object_type":
        """Create an EFLRObject instance based on information found in the config object.

        Args:
            config          :   Config object containing the information on the EFLRObject to be created.
            key             :   Name of the section describing the EFLRObject to be created (e.g. 'Channel-X').
                                If not provided, it is assumed to be the same as the name of the EFLR subclass
                                 (e.g. 'Channel').
            get_if_exists   :   If True and an EFLRObject identified by this section name already exists in the instance
                                dictionary of the given EFLR subclass instance, return that EFLRObject. Otherwise,
                                create a new one, overwriting the existing one in the dictionary.
            set_name        :   Name of the set the EFLRObject belongs to, i.e. name identifying the EFLR subclass
                                instance.


        Returns:
            The created/retrieved EFLRObject instance.
        """

        key = key or cls.eflr_name

        if key not in config.sections():
            raise RuntimeError(f"Section '{key}' not present in the config")

        name_key = "name"

        if name_key not in config[key].keys():
            raise RuntimeError(f"Required item '{name_key}' not present in the config section '{key}'")

        other_kwargs = {k: v for k, v in config[key].items() if k != name_key}

        eflr_instance = cls.get_or_make_eflr(set_name=set_name)
        obj = eflr_instance.make_object_in_this_set(config[key][name_key], **other_kwargs, get_if_exists=get_if_exists)

        for attr in obj.attributes.values():
            if hasattr(attr, 'finalise_from_config'):  # EFLRAttribute; cannot be imported here - circular import issue
                attr.finalise_from_config(config)

        return obj

    def make_all_objects_from_config(cls, config: ConfigParser, keys: Optional[list[str]] = None,
                                     key_pattern: Optional[str] = None, **kwargs) -> list["Self.object_type"]:
        """Create all objects corresponding to given EFLR subclass based on config object information.

        Use 'keys' and/or 'key_pattern' arguments (see below) to limit/precise the set of EFLRObjects created.
        If both are provided, 'key_pattern' is ignored.
        If neither is provided, all config sections whose names begin with the EFLR class name followed by a dash
        will be created.

        Args:
            config      :   Config object containing the information on the objects to be created.
            keys        :   List of config section names identifying the objects to be created.
            key_pattern :   Regex pattern to create a list of section names for objects to be created.
            **kwargs    :   Keyword arguments passed to 'make_object_from_config' for each object.

        Returns:
            List of the created EFLRObject (subclass) instances.
        """

        if keys is not None and key_pattern is not None:
            logger.warning("Both 'keys' and 'key_pattern' arguments provided; ignoring the latter")

        if keys is None:
            if key_pattern is None:
                key_pattern = cls.eflr_name + r"-\w+"
            keys = [key for key in config.sections() if re.compile(key_pattern).fullmatch(key)]

        return [cls.make_object_from_config(config, key=key, **kwargs) for key in keys]


