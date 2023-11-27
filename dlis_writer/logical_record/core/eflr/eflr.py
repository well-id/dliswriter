import logging
import importlib

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode, EFLRType
from dlis_writer.logical_record.core.logical_record import LogicalRecord
from dlis_writer.logical_record.core.eflr.eflr_object import EFLRObject
from dlis_writer.logical_record.core.eflr.eflr_meta import EFLRMeta


logger = logging.getLogger(__name__)


class EFLR(LogicalRecord, metaclass=EFLRMeta):
    """Represents an Explicitly Formatted Logical Record

    Attributes:
        name: Identifier of a Logical Record Segment. Must be
            distinct in a single Logical File.
        set_name: Optional identifier of the set a Logical Record Segment belongs to.

    """

    set_type: str = NotImplemented
    logical_record_type: EFLRType = NotImplemented
    is_eflr = True
    object_type = EFLRObject

    def __init__(self, set_name: str = None):
        super().__init__()

        self.set_name = set_name
        self._set_type_struct = write_struct(RepresentationCode.IDENT, self.set_type)
        self._object_dict = {}
        self._attributes = {}
        self._origin_reference = None

        self._instance_dict[self.set_name] = self

    def __str__(self):
        return f"EFLR class '{self.__class__.__name__}'"

    def clear_object_dict(self):
        self._object_dict.clear()

    @property
    def origin_reference(self):
        return self._origin_reference

    @origin_reference.setter
    def origin_reference(self, val):
        self._origin_reference = val
        for obj in self._object_dict.values():
            obj.origin_reference = val

    @property
    def first_object(self):
        return self._object_dict[next(iter(self._object_dict.keys()))]

    def _make_set_component_bytes(self) -> bytes:
        """Creates component role Set

        Returns:
            Bytes that represent a Set component

        .._RP66 Component Descriptor:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_1
        """

        if self.set_name:
            _bytes = b'\xf8' + self._set_type_struct + write_struct(RepresentationCode.IDENT, self.set_name)
        else:
            _bytes = b'\xf0' + self._set_type_struct

        return _bytes

    def _make_template_bytes(self) -> bytes:
        """Creates template from EFLR object's attributes

        Returns:
            Template bytes compliant with the RP66 V1

        .._RP66 V1 Component Usage:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_2

        """

        _bytes = b''
        for attr in self._attributes.values():
            _bytes += attr.get_as_bytes(for_template=True)

        return _bytes

    def make_body_bytes(self) -> bytes:
        """Writes Logical Record Segment bytes without header"""

        objects = self.get_all_objects()
        if not objects:
            return None

        bts = self._make_set_component_bytes() + self._make_template_bytes()
        for obj in objects:
            bts += obj.make_object_body_bytes()

        return bts

    def make_object_in_this_set(self, name, get_if_exists=False, **kwargs) -> EFLRObject:
        if get_if_exists and name in self._object_dict:
            return self._object_dict[name]

        obj = self.object_type(name, self, **kwargs)
        self._object_dict[name] = obj

        if len(self._object_dict) == 1:
            for attr_name, attr in obj.attributes.items():
                self._attributes[attr_name] = attr.copy()

        obj.origin_reference = self.origin_reference

        return obj

    def get_object(self, *args):
        return self._object_dict.get(*args)

    def get_all_objects(self):
        return list(self._object_dict.values())

    @property
    def n_objects(self):
        return len(self._object_dict)

    @classmethod
    def get_eflr_subclass(cls, object_name):
        module = importlib.import_module('dlis_writer.logical_record.eflr_types')

        class_name = object_name.split('-')[0]
        the_class = getattr(module, class_name, None)
        if the_class is None:
            raise ValueError(f"No EFLR class of name '{class_name}' found")

        return the_class

