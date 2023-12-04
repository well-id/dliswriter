import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any, Union

from dlis_writer.utils.struct_writer import write_struct_obname
from dlis_writer.logical_record.core.attribute.attribute import Attribute

if TYPE_CHECKING:
    from dlis_writer.logical_record.core.eflr.eflr import EFLR


logger = logging.getLogger(__name__)


class EFLRObject:
    """Model an object belonging to an Explicitly Formatted Logical Record - e.g. a particular channel."""

    def __init__(self, name: str, parent: "EFLR", **kwargs):
        """Initialise an EFLRObject.

        Args:
            name        :   Name of the object. This will be the name it is stored with in the created DLIS file.
            parent      :   EFLR instance this object belongs to.
            **kwargs    :   Values to be set in attributes of this object.

        Note:
            When a subclass of EFLRObject is defined, all the attributes should be defined before calling
            super().__init__. This makes it possible for values of attributes to be set here, through 'set_attributes'
            method call.

        """

        self.name = name                #: name of the object
        self.parent = parent            #: EFLR instance this object belongs to

        self.origin_reference: Union[int, None] = None    #: origin reference value, common for records sharing origin
        self.copy_number = 0            #: copy number of the object

        self.set_attributes(**kwargs)

    @property
    def attributes(self) -> dict[str, Attribute]:
        """Attributes defined for this EFLRObject (sub)class with its values for the current instance."""

        return {key: value for key, value in self.__dict__.items() if isinstance(value, Attribute)}

    def __str__(self) -> str:
        """Description of the EFLRObject instance."""

        return f"{self.__class__.__name__} '{self.name}'"

    def __setattr__(self, key: str, value: Any):
        """Limit the possibility of setting attributes by excluding Attribute instances.

        This prevents overwriting Attribute instances being attributes of this EFLRObject. ValueError is raised at such
        attempt. If only a value of the Attribute instance is supposed to be changed, the Attribute's 'value' attribute
        should be used instead.
        """

        if isinstance(getattr(self, key, None), Attribute):
            raise RuntimeError(f"Cannot set DLIS Attribute '{key}'. Did you mean setting '{key}.value' instead?")

        return super().__setattr__(key, value)

    @cached_property
    def obname(self) -> bytes:
        """Create OBNAME bytes of this object - bytes used to identify an object in the file.

        They serve as a reference to the current object - e.g. when a Parameter references a Zone.
        """

        return write_struct_obname(self)

    def _make_attrs_bytes(self) -> bytes:
        """Create bytes describing the values of the EFLRObject instance's Attributes."""

        _bytes = b''
        for attr in self.attributes.values():
            if attr.value is None:
                _bytes += b'\x00'
            else:
                _bytes += attr.get_as_bytes()

        return _bytes

    def make_object_body_bytes(self) -> bytes:
        """Create bytes describing the object: its name and values of its attributes."""

        return b'p' + self.obname + self._make_attrs_bytes()

    def set_attributes(self, **kwargs):
        """Set the values and other characteristics of the EFLRObject's attributes.

        Args:
            **kwargs    :   The mapping of attribute names (and parts) on their values to be set.

        This method allows setting 'value', 'units', and 'representation_code' parts of any attribute of
        the object. The expected syntax for the arguments' keys is <attr_name>.<part_name>, e.g.: 'dimension.value',
        'minimum_value.representation_code', 'minimum_value.units'. It is also possible to use only the attribute name
        as the key (e.g. 'dimension', 'maximum_value'); in this case, the 'value' part of the attribute (dimension.value
        or maximum_value.value respectively) is set to the value of the keyword argument.
        """

        for attr_name, attr_value in kwargs.items():
            attr_name_main, *attr_parts = attr_name.split('.')
            attr_part = attr_parts[0] if attr_parts else 'value'
            if attr_part not in Attribute.settables:
                raise ValueError(f"Cannot set {attr_part} of an Attribute object")

            attr = getattr(self, attr_name_main, None)
            if not attr or not isinstance(attr, Attribute):
                raise AttributeError(f"{self.__class__.__name__} does not have attribute '{attr_name}'")

            logger.debug(f"Setting attribute '{attr_name}' of {self} to {repr(attr_value)}")
            setattr(attr, attr_part, attr_value)
