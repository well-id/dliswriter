import logging
import importlib
from typing import Union, Optional
from typing_extensions import Self

from dlis_writer.utils.struct_writer import write_struct_ascii
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.logical_record import LogicalRecord
from dlis_writer.logical_record.core.eflr.eflr_object import EFLRObject
from dlis_writer.logical_record.core.eflr.eflr_meta import EFLRMeta
from dlis_writer.logical_record.core.attribute import Attribute


logger = logging.getLogger(__name__)


class EFLR(LogicalRecord, metaclass=EFLRMeta):
    """Model an Explicitly Formatted Logical Record."""

    set_type: str = NotImplemented                  #: set type of each particular EFLR (e.g. Channel); see the standard
    logical_record_type: EFLRType = NotImplemented  #: int-enum denoting type of the EFLR
    is_eflr: bool = True                            #: indication that this is an explicitly formatted LR
    object_type: type = EFLRObject                  #: object type which can be held within an EFLR of this type

    _instance_dict: dict[Union[str, None], "EFLR"]

    def __init__(self, set_name: Optional[str] = None):
        """Initialise an EFLR.

        Args:
            set_name    :   Name of the set this EFLR belongs to. Multiple EFLR instances of the same type (subclass)
                            can be included in the same file if their set names differ.
        """

        super().__init__()

        self.set_name = set_name
        self._set_type_struct = write_struct_ascii(self.set_type)  # used in the header
        self._object_dict: dict[str, EFLRObject] = {}  # instances of EFLRObject registered with this EFLR instance
        self._attributes: dict[str, Attribute] = {}   # attributes of this EFLR (cpd from an EFLRObject instance later)
        self._origin_reference: Union[int, None] = None

        self._instance_dict[self.set_name] = self

    def __str__(self) -> str:
        """Represent the EFLR instance as str."""

        return f"{self.__class__.__name__} {repr(self.set_name)}"

    def clear_object_dict(self):
        """Remove all references to EFLRObject instances from the internal dictionary."""

        self._object_dict.clear()

    @property
    def origin_reference(self) -> Union[int, None]:
        """Currently set origin reference of the EFLR instance."""

        return self._origin_reference

    @origin_reference.setter
    def origin_reference(self, val: int):
        """Set origin reference of the EFLR instance and all EFLRObject instances registered with it to a new value."""

        self._origin_reference = val
        for obj in self._object_dict.values():
            obj.origin_reference = val

    @property
    def first_object(self) -> Union["Self.object_type", None]:
        """Return the first EFLRObject instance registered with this EFLR or None if no instances are registered."""

        if not self._object_dict:
            return None

        return self._object_dict[next(iter(self._object_dict.keys()))]

    def _make_set_component_bytes(self) -> bytes:
        """Create bytes describing the set of this EFLR, using set type (class attr) and name (specified at init)."""

        if self.set_name:
            _bytes = b'\xf8' + self._set_type_struct + write_struct_ascii(self.set_name)
        else:
            _bytes = b'\xf0' + self._set_type_struct

        return _bytes

    def _make_template_bytes(self) -> bytes:
        """Create bytes describing the attribute template of this EFLR.

        Note: if no EFLRObjects are registered, this will return an empty bytes object."""

        _bytes = b''
        for attr in self._attributes.values():
            _bytes += attr.get_as_bytes(for_template=True)

        return _bytes

    def _make_body_bytes(self) -> bytes:
        """Create bytes describing the body of this EFLR - the values of attributes of the registered EFLRObjects.

        If no EFLRObjects are registered, this will return an empty bytes object.
        """

        objects = self.get_all_objects()
        if not objects:
            return b''

        bts = self._make_set_component_bytes() + self._make_template_bytes()
        for obj in objects:
            bts += obj.make_object_body_bytes()

        return bts

    def make_object_in_this_set(self, name: str, get_if_exists: bool = False, **kwargs) -> EFLRObject:
        """Make an EFLRObject according the specifications and register it with this EFLR instance.

        Args:
            name            :   Name of the object to be created.
            get_if_exists   :   If True and an object of the same name already exists in the internal object dictionary,
                                return the existing object rather than overwriting it with a new one.
            kwargs          :   Keyword arguments passed to initialisation of the object - e.g. setting the values
                                of its attributes.
        """

        if get_if_exists and name in self._object_dict:
            return self._object_dict[name]

        obj = self.object_type(name, parent=self, **kwargs)
        self._object_dict[name] = obj

        if len(self._object_dict) == 1:
            for attr_name, attr in obj.attributes.items():
                self._attributes[attr_name] = attr.copy()

        obj.origin_reference = self.origin_reference

        return obj

    def get_all_objects(self) -> list[EFLRObject]:
        """Return a list of all EFLRObject instances registered with this EFLR instance."""

        return list(self._object_dict.values())

    @property
    def n_objects(self) -> int:
        """Number of EFLRObject instances registered with this EFLR instance."""

        return len(self._object_dict)

    @classmethod
    def get_eflr_subclass(cls, object_name: str) -> EFLRMeta:
        """Retrieve an EFLR subclass based on the provided object name.

        This method is meant to be used with names of sections of a config object. The names are expected to take
        the form: '<class-name>-<individual-name>', e.g. 'Channel-amplitude', 'Zone-4', etc.
        """

        module = importlib.import_module('dlis_writer.logical_record.eflr_types')

        class_name = object_name.split('-')[0]
        the_class = getattr(module, class_name, None)
        if the_class is None:
            raise ValueError(f"No EFLR class of name '{class_name}' found")

        return the_class

