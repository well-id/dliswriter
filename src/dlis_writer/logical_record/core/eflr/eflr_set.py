import logging
from typing import Union, Optional, Any

from dlis_writer.utils.struct_writer import write_struct_ascii
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.logical_record import LogicalRecord
from dlis_writer.logical_record.core.eflr.eflr_item import EFLRItem
from dlis_writer.logical_record.core.eflr.eflr_set_meta import EFLRSetMeta
from dlis_writer.logical_record.core.attribute import Attribute


logger = logging.getLogger(__name__)


class EFLRSet(LogicalRecord, metaclass=EFLRSetMeta):
    """Model an Explicitly Formatted Logical Record."""

    set_type: str = NotImplemented                  #: set type of each particular EFLR (e.g. Channel); see the standard
    logical_record_type: EFLRType = NotImplemented  #: int-enum denoting type of the EFLR
    is_eflr: bool = True                            #: indication that this is an explicitly formatted LR
    item_type: type[EFLRItem] = EFLRItem            #: EFLRItem subclass which can be held within this EFLRTable type

    _eflr_set_instance_dict: dict[Union[str, None], "EFLRSet"]

    def __init__(self, set_name: Optional[str] = None):
        """Initialise an EFLRTable.

        Args:
            set_name    :   Name of the set this EFLR belongs to. Multiple EFLRSet instances of the same type
                            (subclass) can be included in the same file if their set names differ.
        """

        super().__init__()

        self.set_name = set_name
        self._set_type_struct = write_struct_ascii(self.set_type)  # used in the header
        self._eflr_item_list: list[EFLRItem] = []  # instances of EFLRItem registered with this EFLRSet instance
        self._attributes: dict[str, Attribute] = {}   # attributes of this EFLRSet (cpd from an EFLRItem instance)
        self._origin_reference: Union[int, None] = None

        self._eflr_set_instance_dict[self.set_name] = self

    def __str__(self) -> str:
        """Represent the EFLRSet instance as str."""

        return f"{self.__class__.__name__} {repr(self.set_name)}"

    def clear_eflr_item_list(self) -> None:
        """Remove all references to EFLRItem instances from the internal dictionary."""

        self._eflr_item_list.clear()

    @property
    def origin_reference(self) -> Union[int, None]:
        """Currently set origin reference of the EFLRSet instance."""

        return self._origin_reference

    @origin_reference.setter
    def origin_reference(self, val: int) -> None:
        """Set a new origin reference of the EFLRSet instance and all EFLRItem instances registered with it."""

        self._origin_reference = val
        for obj in self._eflr_item_list:
            obj.origin_reference = val

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
        """Create bytes describing the body of this EFLRSet - the values of attributes of the registered EFLRItems.

        If no EFLRItems are registered, this will return an empty bytes object.
        """

        eflr_items = self.get_all_eflr_items()
        if not eflr_items:
            return b''

        bts = self._make_set_component_bytes() + self._make_template_bytes()
        for ei in eflr_items:
            bts += ei.make_item_body_bytes()

        return bts

    def register_item(self, child: EFLRItem) -> None:
        """Register a child EFLRItem with this EFLRSet."""

        if not isinstance(child, self.item_type):
            raise TypeError(f"Expected an instance of {self.item_type}; got {type(child)}: {child}")

        self._eflr_item_list.append(child)

        if len(self._eflr_item_list) == 1:
            for attr_name, attr in child.attributes.items():
                self._attributes[attr_name] = attr.copy()

        child.origin_reference = self.origin_reference

    def get_all_eflr_items(self) -> list[EFLRItem]:
        """Return a list of all EFLRItem instances registered with this EFLRSet instance."""

        return self._eflr_item_list[:]  # copy

    @property
    def n_items(self) -> int:
        """Number of EFLRItem instances registered with this EFLRSet instance."""

        return len(self._eflr_item_list)

    @classmethod
    def clear_set_instance_dict(cls) -> None:
        """Remove all instances of the EFLRSet (sub)class from the internal dictionary."""

        if cls._eflr_set_instance_dict:
            logger.debug(f"Removing all defined instances of {cls.__name__}")
            cls._eflr_set_instance_dict.clear()

    @classmethod
    def get_or_make_set(cls, set_name: Optional[str] = None) -> "EFLRSet":
        """Retrieve an EFLRSet instance with given set name from the internal dict or create one."""

        if set_name in cls._eflr_set_instance_dict:
            return cls._eflr_set_instance_dict[set_name]

        return cls(set_name)

    @classmethod
    def get_all_sets(cls) -> list["EFLRSet"]:
        """Return a list of all EFLRSet (subclass) instances which are stored in the internal dictionary."""

        return list(cls._eflr_set_instance_dict.values())
