import logging
from typing import Union, Optional

from dlis_writer.utils.struct_writer import write_struct_ascii
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.logical_record import LogicalRecord
from dlis_writer.logical_record.core.eflr.eflr_item import EFLRItem
from dlis_writer.logical_record.core.attribute import Attribute


logger = logging.getLogger(__name__)


class EFLRSet(LogicalRecord):
    """Model an Explicitly Formatted Logical Record."""

    set_type: str = NotImplemented                  #: set type of each particular EFLR (e.g. Channel); see the standard
    logical_record_type: EFLRType = NotImplemented  #: int-enum denoting type of the EFLR
    is_eflr: bool = True                            #: indication that this is an explicitly formatted LR
    item_type: type[EFLRItem] = EFLRItem            #: EFLRItem subclass which can be held within this EFLRTable type

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
        self._origin_reference: Union[int, None] = None

    def __str__(self) -> str:
        """Represent the EFLRSet instance as str."""

        return f"{self.__class__.__name__} {repr(self.set_name)}"

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
        if self._eflr_item_list:
            child0 = self._eflr_item_list[0]
            for attr in child0.attributes.values():
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

        child.origin_reference = self.origin_reference

    def get_all_eflr_items(self) -> list[EFLRItem]:
        """Return a list of all EFLRItem instances registered with this EFLRSet instance."""

        return self._eflr_item_list[:]  # copy

    @property
    def n_items(self) -> int:
        """Number of EFLRItem instances registered with this EFLRSet instance."""

        return len(self._eflr_item_list)
