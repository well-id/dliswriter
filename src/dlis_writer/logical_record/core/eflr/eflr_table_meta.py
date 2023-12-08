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
    """Define a metaclass for EFLRTable..

    The main motivation for defining this metaclass is to be able to use an instance dictionary (see _instance_dict
    in __new__), which is separate for each subclass of EFLRTable.

    In addition, this metaclass implements several class methods of EFLRTable, mostly related to creating EFLRTable
    and EFLRItem instances, e.g. from a config object.
    """

    _eflr_table_instance_dict: dict[Union[str, None], "EFLRTable"]
    item_type: type
    eflr_name: str
    eflr_name_pattern = re.compile(r'(?P<name>\w+)Table')

    def __new__(cls, *args, **kwargs) -> "EFLRTableMeta":
        """Create a new EFLRTable class (instance of EFLRMeta).

        All positional and keyword arguments are passed to the super-metaclass: LRMeta.
        """

        obj = super().__new__(cls, *args, **kwargs)
        obj._eflr_table_instance_dict = {}
        obj.eflr_name = cls.eflr_name_pattern.fullmatch(obj.__name__).group('name')
        return obj

    def clear_eflr_table_instance_dict(cls):
        """Remove all instances of the EFLRTable (sub)class from the internal dictionary."""

        if cls._eflr_table_instance_dict:
            logger.debug(f"Removing all defined instances of {cls.__name__}")
            cls._eflr_table_instance_dict.clear()

    def get_or_make_eflr_table(cls, set_name: Optional[str] = None) -> "EFLRTable":
        """Retrieve an EFLRTable instance with given set name from the internal dict or create one."""

        if set_name in cls._eflr_table_instance_dict:
            return cls._eflr_table_instance_dict[set_name]

        return cls(set_name)

    def get_all_eflr_table_instances(cls) -> list["EFLRTable"]:
        """Return a list of all EFLRTable (subclass) instances which are stored in the internal dictionary."""

        return list(cls._eflr_table_instance_dict.values())

    def make_eflr_item_from_config(cls, config: ConfigParser, key: Optional[str] = None, get_if_exists: bool = False,
                                   set_name: Optional[str] = None) -> "Self.item_type":
        """Create an EFLRItem instance based on information found in the config object.

        Args:
            config          :   Config object containing the information on the EFLRItem to be created.
            key             :   Name of the section describing the EFLRItem to be created (e.g. 'Channel-X').
                                If not provided, it is assumed to be the same as the name of the EFLRTable subclass
                                 (e.g. 'Channel').
            get_if_exists   :   If True and an EFLRItem identified by this section name already exists in the instance
                                dictionary of the given EFLRTable subclass instance, return that EFLRItem. Otherwise,
                                create a new one, overwriting the existing one in the dictionary.
            set_name        :   Name of the set the EFLRItem belongs to, i.e. name identifying the EFLRTable subclass
                                instance.


        Returns:
            The created/retrieved EFLRItem instance.
        """

        key = key or cls.eflr_name

        if key not in config.sections():
            raise RuntimeError(f"Section '{key}' not present in the config")

        name_key = "name"

        if name_key not in config[key].keys():
            raise RuntimeError(f"Required item '{name_key}' not present in the config section '{key}'")

        other_kwargs = {k: v for k, v in config[key].items() if k != name_key}

        item_name = config[key][name_key]
        eflr_table = cls.get_or_make_eflr_table(set_name=set_name)
        eflr_item = None
        if get_if_exists:
            eflr_item = eflr_table.get_eflr_item(item_name, None)
        if eflr_item is None:
            eflr_item = eflr_table.item_type(item_name, parent=eflr_table, **other_kwargs)

        for attr in eflr_item.attributes.values():
            if hasattr(attr, 'finalise_from_config'):  # EFLRAttribute; cannot be imported here - circular import issue
                attr.finalise_from_config(config)

        return eflr_item

    def make_all_eflr_items_from_config(cls, config: ConfigParser, keys: Optional[list[str]] = None,
                                        key_pattern: Optional[str] = None, **kwargs) -> list["Self.item_type"]:
        """Create all items corresponding to given EFLRTable subclass based on config object information.

        Use 'keys' and/or 'key_pattern' arguments (see below) to limit/precise the set of EFLRItems created.
        If both are provided, 'key_pattern' is ignored.
        If neither is provided, all config sections whose names begin with the EFLRTable class name followed by a dash
        will be created.

        Args:
            config      :   Config object containing the information on the objects to be created.
            keys        :   List of config section names identifying the objects to be created.
            key_pattern :   Regex pattern to create a list of section names for objects to be created.
            **kwargs    :   Keyword arguments passed to 'make_eflr_item_from_config' for each item.

        Returns:
            List of the created EFLRItem (subclass) instances.
        """

        if keys is not None and key_pattern is not None:
            logger.warning("Both 'keys' and 'key_pattern' arguments provided; ignoring the latter")

        if keys is None:
            if key_pattern is None:
                key_pattern = cls.eflr_name + r"-\w+"
            keys = [key for key in config.sections() if re.compile(key_pattern).fullmatch(key)]

        return [cls.make_eflr_item_from_config(config, key=key, **kwargs) for key in keys]


