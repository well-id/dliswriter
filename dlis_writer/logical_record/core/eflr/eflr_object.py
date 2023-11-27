import logging
from functools import cached_property
from typing import TYPE_CHECKING

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.attribute.attribute import Attribute

if TYPE_CHECKING:
    from dlis_writer.logical_record.core.eflr.eflr import EFLR


logger = logging.getLogger(__name__)


class EFLRObject:
    def __init__(self, name: str, parent: "EFLR", **kwargs):
        self.name = name
        self.parent = parent

        self.origin_reference = None
        self.copy_number = 0

        self.set_attributes(**kwargs)

    @property
    def attributes(self):
        return {key: value for key, value in self.__dict__.items() if isinstance(value, Attribute)}

    def __str__(self):
        return f"{self.__class__.__name__} '{self.name}'"

    def __setattr__(self, key, value):
        if isinstance(getattr(self, key, None), Attribute):
            raise RuntimeError(f"Cannot set DLIS Attribute '{key}'. Did you mean setting '{key}.value' instead?")

        return super().__setattr__(key, value)

    @cached_property
    def obname(self) -> bytes:
        """Creates OBNAME bytes according to RP66 V1 spec

        Returns:
            OBNAME bytes that is used to identify an object in RP66 V1

        .._RP66 V1 OBNAME Representation Code:
            http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_23
        """

        return write_struct(RepresentationCode.OBNAME, self)

    def _make_attrs_bytes(self) -> bytes:
        """Creates object bytes that follows the object component

        Note:
            Each attribute of EFLR object is a logical_record.utils.core.Attribute instance
            Using Attribute instances' get_as_bytes method to create bytes.

        """

        _bytes = b''
        for attr in self.attributes.values():
            if attr.value is None:
                _bytes += b'\x00'
            else:
                _bytes += attr.get_as_bytes()

        return _bytes

    def make_object_body_bytes(self):
        return b'p' + self.obname + self._make_attrs_bytes()

    def set_attributes(self, **kwargs):
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
