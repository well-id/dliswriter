import re
from configparser import ConfigParser
import logging
import importlib

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode, EFLRType
from dlis_writer.logical_record.core.attribute.attribute import Attribute
from dlis_writer.logical_record.core.logical_record import LogicalRecord


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

    @property
    def obname(self) -> bytes:
        """Creates OBNAME bytes according to RP66 V1 spec

        Returns:
            OBNAME bytes that is used to identify an object in RP66 V1

        .._RP66 V1 OBNAME Representation Code:
            http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_23
        """

        return write_struct(RepresentationCode.OBNAME, self)

    def _make_obname_bytes(self) -> bytes:
        """Creates object component"""

        return b'p' + self.obname

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
        return self._make_obname_bytes() + self._make_attrs_bytes()
    
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


class EFLR(LogicalRecord):
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

    def __str__(self):
        return f"EFLR class '{self.__class__.__name__}'"
    
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
        for attr in self.attributes.values():
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

    def make_object(self, name, **kwargs) -> EFLRObject:
        obj = self.object_type(name, self, **kwargs)
        self._object_dict[name] = obj

        if len(self._object_dict) == 1:
            for attr_name, attr in obj.attributes.items():
                self._attributes[attr_name] = attr.copy()

        return obj

    def make_object_from_config(self, config: ConfigParser, key=None) -> EFLRObject:
        key = key or self.__class__.__name__

        if key not in config.sections():
            raise RuntimeError(f"Section '{key}' not present in the config")

        name_key = "name"

        if name_key not in config[key].keys():
            raise RuntimeError(f"Required item '{name_key}' not present in the config section '{key}'")

        other_kwargs = {k: v for k, v in config[key].items() if k != name_key}

        return self.make_object(config[key][name_key], **other_kwargs)

    def get_or_make_all_from_config(self, config: ConfigParser, keys: list[str] = None, key_pattern: str = None):
        if not keys:
            if key_pattern is None:
                key_pattern = self.__class__.__name__ + r"-\w+"
            key_pattern = re.compile(key_pattern)
            keys = [key for key in config.sections() if key_pattern.fullmatch(key)]

        return [self.get_or_make_from_config(key, config) for key in keys]
    
    def get_object(self, name):
        return self._object_dict.get(name)

    def get_all_objects(self):
        return list(self._object_dict.values())

    def clear_objects(self):
        if self._object_dict:
            logger.debug(f"Removing all defined objects of {self}")
            self._object_dict.clear()

    def get_or_make_from_config(self, name, config):
        if name in self._object_dict:
            return self.get_object(name)

        if name in config.sections():
            if (object_name := config[name].get('name', None)) in self._object_dict:
                return self.get_object(object_name)

        return self.make_object_from_config(config, key=name)

    @classmethod
    def get_object_class(cls, object_name):
        module = importlib.import_module('dlis_writer.logical_record.eflr_types')

        class_name = object_name.split('-')[0]
        the_class = getattr(module, class_name, None)
        if the_class is None:
            raise ValueError(f"No EFLR class of name '{class_name}' found")

        return the_class

