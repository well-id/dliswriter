import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any, Union, Optional, Generator

from dlis_writer.utils.struct_writer import write_struct_obname
from dlis_writer.logical_record.core.attribute.attribute import Attribute

if TYPE_CHECKING:
    from dlis_writer.logical_record.core.eflr.eflr_set import EFLRSet


logger = logging.getLogger(__name__)


class AttrSetup:
    """Convenience class to pass setup for an Attribute without creating a dictionary."""

    # Note: the initial plan was to make it a dataclass, but this doesn't give the PyCharm IDE typing hints,
    # which is one of the main points of this class

    def __init__(self, value: Optional[Any] = None, units: Optional[str] = None) -> None:
        """Initialise AttrSetup with any of the passed values."""

        self.value = value
        self.units = units
        # Note: no checks done here, because they're done in EFLRItem/Attribute later anyway

    def items(self) -> Generator:
        for item_name in ('value', 'units'):
            if (item_value := getattr(self, item_name)) is not None:
                yield item_name, item_value


class EFLRItem:
    """Model an item belonging to an Explicitly Formatted Logical Record - e.g. a particular channel."""

    parent_eflr_class: type["EFLRSet"] = NotImplemented

    def __init__(self, name: str, parent: Optional["EFLRSet"] = None, set_name: Optional[str] = None,
                 **kwargs: Any) -> None:
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
        self._copy_number = self._compute_copy_number()    #: copy number of the item - ith EFLRItem of the same name

        for attribute in self.attributes.values():
            attribute.parent_eflr = self

        self.set_attributes(**{k: v for k, v in kwargs.items() if v is not None})

    @property
    def copy_number(self) -> int:
        """Copy number of this EFLRItem."""

        return self._copy_number

    def _compute_copy_number(self) -> int:
        """Compute copy number of this ELFRItem, i.e. how many other objects of the same type and name there are."""

        items_with_the_same_name = filter(lambda o: o.name == self.name, self.parent.get_all_eflr_items_from_all_sets())
        return len(list(items_with_the_same_name)) - 1

    @classmethod
    def _get_parent(cls, parent: Optional["EFLRSet"] = None, set_name: Optional[str] = None) -> "EFLRSet":
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

        return cls.parent_eflr_class.get_or_make_set(set_name=set_name)

    @property
    def attributes(self) -> dict[str, Attribute]:
        """Attributes defined for this EFLRItem (sub)class with its values for the current instance."""

        return {key: value for key, value in self.__dict__.items() if isinstance(value, Attribute)}

    def __str__(self) -> str:
        """Description of the EFLRItem instance."""

        return f"{self.__class__.__name__} '{self.name}'"

    def __setattr__(self, key: str, value: Any) -> None:
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

    def _set_defaults(self) -> None:
        """Called before writing the item's bytes. Set default values to some attributes if they were not set at all."""

        pass

    def make_item_body_bytes(self) -> bytes:
        """Create bytes describing the item: its name and values of its attributes."""

        self._set_defaults()

        return b'p' + self.obname + self._make_attrs_bytes()

    def set_attributes(self, **kwargs: Any) -> None:
        """Set the values and other characteristics of the EFLRItem's attributes.

        Args:
            **kwargs    :   The mapping of attribute names (and parts) on their values to be set.

        This method allows setting 'value', 'units', and 'representation_code' parts of any attribute of
        the item. The expected syntax for the arguments' keys is <attr_name>.<part_name>, e.g.: 'dimension.value',
        'minimum_value.representation_code', 'minimum_value.units'. It is also possible to use only the attribute name
        as the key (e.g. 'dimension', 'maximum_value'); in this case, the 'value' part of the attribute (dimension.value
        or maximum_value.value respectively) is set to the value of the keyword argument.
        """

        def set_value(_attr: Attribute, _value: Any, _key: str = 'value'):
            logger.debug(f"Setting {_attr.label}.{_key} of {self} to {repr(_value)}")
            setattr(_attr, _key, _value)

        for attr_name, attr_value in kwargs.items():
            attr = getattr(self, attr_name, None)
            if not attr or not isinstance(attr, Attribute):
                raise AttributeError(f"{self.__class__.__name__} does not have attribute '{attr_name}'")

            if isinstance(attr_value, (dict, AttrSetup)):
                for key, value in attr_value.items():
                    if key not in attr.settables:
                        raise ValueError(f"Cannot set {key} of a(n) {attr.__class__.__name__}")
                    set_value(attr, value, key)

            else:
                set_value(attr, attr_value)

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
