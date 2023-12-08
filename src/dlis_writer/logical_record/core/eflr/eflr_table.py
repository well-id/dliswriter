import re
import logging
import importlib
from typing import Union, Optional, Any
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.utils.struct_writer import write_struct_ascii
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.logical_record import LogicalRecord
from dlis_writer.logical_record.core.eflr.eflr_item import EFLRItem
from dlis_writer.logical_record.core.eflr.eflr_table_meta import EFLRTableMeta
from dlis_writer.logical_record.core.attribute import Attribute


logger = logging.getLogger(__name__)


class EFLRTable(LogicalRecord, metaclass=EFLRTableMeta):
    """Model an Explicitly Formatted Logical Record."""

    set_type: str = NotImplemented                  #: set type of each particular EFLR (e.g. Channel); see the standard
    logical_record_type: EFLRType = NotImplemented  #: int-enum denoting type of the EFLR
    is_eflr: bool = True                            #: indication that this is an explicitly formatted LR
    item_type: type = EFLRItem                      #: EFLRItem subclass which can be held within this EFLRTable type

    _eflr_table_instance_dict: dict[Union[str, None], "EFLRTable"]

    def __init__(self, set_name: Optional[str] = None):
        """Initialise an EFLRTable.

        Args:
            set_name    :   Name of the set this EFLR belongs to. Multiple EFLRTable instances of the same type
                            (subclass) can be included in the same file if their set names differ.
        """

        super().__init__()

        self.set_name = set_name
        self._set_type_struct = write_struct_ascii(self.set_type)  # used in the header
        self._eflr_item_dict: dict[str, EFLRItem] = {}  # instances of EFLRItem registered with this EFLRTable instance
        self._attributes: dict[str, Attribute] = {}   # attributes of this EFLRTable (cpd from an EFLRItem instance)
        self._origin_reference: Union[int, None] = None

        self._eflr_table_instance_dict[self.set_name] = self

    def __str__(self) -> str:
        """Represent the EFLRTable instance as str."""

        return f"{self.__class__.__name__} {repr(self.set_name)}"

    def clear_eflr_item_dict(self):
        """Remove all references to EFLRItem instances from the internal dictionary."""

        self._eflr_item_dict.clear()

    @property
    def origin_reference(self) -> Union[int, None]:
        """Currently set origin reference of the EFLRTable instance."""

        return self._origin_reference

    @origin_reference.setter
    def origin_reference(self, val: int):
        """Set a new origin reference of the EFLRTable instance and all EFLRItem instances registered with it."""

        self._origin_reference = val
        for obj in self._eflr_item_dict.values():
            obj.origin_reference = val

    @property
    def first_item(self) -> Union["Self.item_type", None]:
        """Return the first EFLRItem instance registered with this EFLRTable or None if no instances are registered."""

        if not self._eflr_item_dict:
            return None

        return self._eflr_item_dict[next(iter(self._eflr_item_dict.keys()))]

    def _make_set_component_bytes(self) -> bytes:
        """Create bytes describing the set of this EFLR, using set type (class attr) and name (specified at init)."""

        if self.set_name:
            _bytes = b'\xf8' + self._set_type_struct + write_struct_ascii(self.set_name)
        else:
            _bytes = b'\xf0' + self._set_type_struct

        return _bytes

    def _make_template_bytes(self) -> bytes:
        """Create bytes describing the attribute template of this EFLR.

        Note: if no EFLRItems are registered, this will return an empty bytes object."""

        _bytes = b''
        for attr in self._attributes.values():
            _bytes += attr.get_as_bytes(for_template=True)

        return _bytes

    def _make_body_bytes(self) -> bytes:
        """Create bytes describing the body of this EFLRTable - the values of attributes of the registered EFLRItems.

        If no EFLRItems are registered, this will return an empty bytes object.
        """

        eflr_items = self.get_all_eflr_items()
        if not eflr_items:
            return b''

        bts = self._make_set_component_bytes() + self._make_template_bytes()
        for ei in eflr_items:
            bts += ei.make_item_body_bytes()

        return bts

    def get_eflr_item(self, name: str, *args: Any) -> Union[EFLRItem, Any]:
        """Get an EFLRItem instance from the internal dict by its name.

        Args:
            name    :   Name of the EFLR item (under which it was registered).
            *args   :   A maximum of 1 arg is allowed. It is used as the fallback value if the item is not found.
        """

        return self._eflr_item_dict.get(name, *args)

    def register_item(self, child: EFLRItem):
        """Register a child EFLRItem with this EFLRTable."""

        if not isinstance(child, self.item_type):
            raise TypeError(f"Expected an instance of {self.item_type}; got {type(child)}: {child}")

        self._eflr_item_dict[child.name] = child

        if len(self._eflr_item_dict) == 1:
            for attr_name, attr in child.attributes.items():
                self._attributes[attr_name] = attr.copy()

        child.origin_reference = self.origin_reference

    def get_all_eflr_items(self) -> list[EFLRItem]:
        """Return a list of all EFLRItem instances registered with this EFLRTable instance."""

        return list(self._eflr_item_dict.values())

    @property
    def n_items(self) -> int:
        """Number of EFLRItem instances registered with this EFLRTable instance."""

        return len(self._eflr_item_dict)

    @classmethod
    def get_eflr_subclass(cls, object_name: str) -> EFLRTableMeta:
        """Retrieve an EFLRTable subclass based on the provided object name.

        This method is meant to be used with names of sections of a config object. The names are expected to take
        the form: '<class-name>-<individual-name>', e.g. 'Channel-amplitude', 'Zone-4', etc.
        """

        module = importlib.import_module('dlis_writer.logical_record.eflr_types')

        class_name = object_name.split('-')[0] + 'Table'
        the_class = getattr(module, class_name, None)
        if the_class is None:
            raise ValueError(f"No EFLRTable class of name '{class_name}' found")

        return the_class

    @classmethod
    def clear_eflr_table_instance_dict(cls):
        """Remove all instances of the EFLRTable (sub)class from the internal dictionary."""

        if cls._eflr_table_instance_dict:
            logger.debug(f"Removing all defined instances of {cls.__name__}")
            cls._eflr_table_instance_dict.clear()

    @classmethod
    def get_or_make_eflr_table(cls, set_name: Optional[str] = None) -> "EFLRTable":
        """Retrieve an EFLRTable instance with given set name from the internal dict or create one."""

        if set_name in cls._eflr_table_instance_dict:
            return cls._eflr_table_instance_dict[set_name]

        return cls(set_name)

    @classmethod
    def get_all_eflr_table_instances(cls) -> list["EFLRTable"]:
        """Return a list of all EFLRTable (subclass) instances which are stored in the internal dictionary."""

        return list(cls._eflr_table_instance_dict.values())

    @classmethod
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

        return [cls.item_type.from_config(config, key=key, **kwargs) for key in keys]


