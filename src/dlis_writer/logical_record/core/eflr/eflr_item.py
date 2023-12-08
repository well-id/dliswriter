import re
import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any, Union, Optional
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.utils.struct_writer import write_struct_obname
from dlis_writer.logical_record.core.attribute.attribute import Attribute

if TYPE_CHECKING:
    from dlis_writer.logical_record.core.eflr.eflr_table import EFLRTable


logger = logging.getLogger(__name__)


class EFLRItem:
    """Model an item belonging to an Explicitly Formatted Logical Record - e.g. a particular channel."""

    parent_eflr_class: type["EFLRTable"] = NotImplemented

    def __init__(self, name: str, parent: Optional["EFLRTable"] = None, set_name: Optional[str] = None, **kwargs):
        """Initialise an EFLRItem.

        Args:
            name        :   Name of the item. This will be the name it is stored with in the created DLIS file.
            parent      :   EFLRTable instance this item belongs to. If not provided, retrieved/made based on set_name.
            set_name    :   Set name of the parent EFLRTable instance.
            **kwargs    :   Values to be set in attributes of this item.

        Note:
            When a subclass of EFLRItem is defined, all the attributes should be defined before calling
            super().__init__. This makes it possible for values of attributes to be set here, through 'set_attributes'
            method call.

        """

        self.name = name    #: name of the item
        self.parent = self._get_parent(parent=parent, set_name=set_name)  #: EFLRTable instance this item belongs to
        self.parent.register_item(self)

        self.origin_reference: Union[int, None] = None    #: origin reference value, common for records sharing origin
        self.copy_number = 0            #: copy number of the item

        self.set_attributes(**{k: v for k, v in kwargs.items() if v is not None})

    @classmethod
    def _get_parent(cls, parent: Optional["EFLRTable"] = None, set_name: Optional[str] = None) -> "EFLRTable":
        """Validate, retrieve, or create a parent EFLRTable instance.

        Args:
            parent      :   Parent EFLRTable instance. If not provided, set_name will be used to retrieve/make one.
            set_name    :   Set name of the parent EFLRTable instance. If parent is provided, it is checked against its
                            set_name.

        Returns:
            The parent EFLRTable instance.
        """

        if parent is not None:
            if not isinstance(parent, cls.parent_eflr_class):
                raise TypeError(f"Expected an instance of {cls.parent_eflr_class.__name__}; "
                                f"got a {type(parent)}: {parent}")
            if parent.set_name != set_name and set_name is not None:
                raise ValueError(f"The provided set name: {set_name} does not match the set name of the "
                                 f"provided parent EFLRTable: {parent.set_name}")

            return parent

        return cls.parent_eflr_class.get_or_make_eflr_table(set_name=set_name)

    @property
    def attributes(self) -> dict[str, Attribute]:
        """Attributes defined for this EFLRItem (sub)class with its values for the current instance."""

        return {key: value for key, value in self.__dict__.items() if isinstance(value, Attribute)}

    def __str__(self) -> str:
        """Description of the EFLRItem instance."""

        return f"{self.__class__.__name__} '{self.name}'"

    def __setattr__(self, key: str, value: Any):
        """Limit the possibility of setting attributes by excluding Attribute instances.

        This prevents overwriting Attribute instances being attributes of this EFLRItem. ValueError is raised at such
        attempt. If only a value of the Attribute instance is supposed to be changed, the Attribute's 'value' attribute
        should be used instead.
        """

        if isinstance(getattr(self, key, None), Attribute):
            raise RuntimeError(f"Cannot set DLIS Attribute '{key}'. Did you mean setting '{key}.value' instead?")

        return super().__setattr__(key, value)

    @cached_property
    def obname(self) -> bytes:
        """Create OBNAME bytes of this item - bytes used to identify an item in the file.

        They serve as a reference to the current item - e.g. when a Parameter references a Zone.
        """

        return write_struct_obname(self)

    def _make_attrs_bytes(self) -> bytes:
        """Create bytes describing the values of the EFLRItem instance's Attributes."""

        _bytes = b''
        for attr in self.attributes.values():
            if attr.value is None:
                _bytes += b'\x00'
            else:
                _bytes += attr.get_as_bytes()

        return _bytes

    def make_item_body_bytes(self) -> bytes:
        """Create bytes describing the item: its name and values of its attributes."""

        return b'p' + self.obname + self._make_attrs_bytes()

    def set_attributes(self, **kwargs):
        """Set the values and other characteristics of the EFLRItem's attributes.

        Args:
            **kwargs    :   The mapping of attribute names (and parts) on their values to be set.

        This method allows setting 'value', 'units', and 'representation_code' parts of any attribute of
        the item. The expected syntax for the arguments' keys is <attr_name>.<part_name>, e.g.: 'dimension.value',
        'minimum_value.representation_code', 'minimum_value.units'. It is also possible to use only the attribute name
        as the key (e.g. 'dimension', 'maximum_value'); in this case, the 'value' part of the attribute (dimension.value
        or maximum_value.value respectively) is set to the value of the keyword argument.
        """

        for attr_name, attr_value in kwargs.items():
            attr_name_main, *attr_parts = attr_name.split('.')
            attr_part = attr_parts[0] if attr_parts else 'value'
            if attr_part not in Attribute.settables:
                raise ValueError(f"Cannot set {attr_part} of an Attribute item")

            attr = getattr(self, attr_name_main, None)
            if not attr or not isinstance(attr, Attribute):
                raise AttributeError(f"{self.__class__.__name__} does not have attribute '{attr_name}'")

            logger.debug(f"Setting attribute '{attr_name}' of {self} to {repr(attr_value)}")
            setattr(attr, attr_part, attr_value)

    @classmethod
    def convert_maybe_numeric(cls, val: Union[str, int, float]) -> Union[str, int, float]:
        """Try converting a value to a number. If that fails, return the value unchanged."""

        if isinstance(val, (int, float)):
            return val

        if not isinstance(val, str):
            raise TypeError(f"Expected an int, float, or str; got {type(val)}: {val}")
        try:
            return cls.convert_numeric(val)
        except ValueError:
            pass
        return val

    @staticmethod
    def convert_numeric(value: str) -> Union[int, float, str]:
        """Convert a string to an integer or float."""

        parser = float if '.' in value else int

        try:
            value = parser(value)
        except ValueError:
            raise ValueError(f"Value '{value}' could not be converted to a numeric type")
        return value

    @classmethod
    def from_config(cls, config: ConfigParser, key: Optional[str] = None, get_if_exists: bool = False,
                    set_name: Optional[str] = None) -> Self:
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

        key = key or cls.parent_eflr_class.eflr_name

        if key not in config.sections():
            raise RuntimeError(f"Section '{key}' not present in the config")

        name_key = "name"

        if name_key not in config[key].keys():
            raise RuntimeError(f"Required item '{name_key}' not present in the config section '{key}'")

        other_kwargs = {k: v for k, v in config[key].items() if k != name_key}

        item_name = config[key][name_key]
        eflr_table = cls.parent_eflr_class.get_or_make_eflr_table(set_name=set_name)
        eflr_item = None
        if get_if_exists:
            eflr_item = eflr_table.get_eflr_item(item_name, None)
        if eflr_item is None:
            eflr_item = cls(item_name, parent=eflr_table, **other_kwargs)

        for attr in eflr_item.attributes.values():
            if hasattr(attr, 'finalise_from_config'):  # EFLRAttribute; cannot be imported here - circular import issue
                attr.finalise_from_config(config)

        return eflr_item

    @classmethod
    def all_from_config(cls, config: ConfigParser, keys: Optional[list[str]] = None,
                        key_pattern: Optional[str] = None, **kwargs) -> list[Self]:
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
                key_pattern = cls.parent_eflr_class.eflr_name + r"-\w+"
            keys = [key for key in config.sections() if re.compile(key_pattern).fullmatch(key)]

        return [cls.from_config(config, key=key, **kwargs) for key in keys]

