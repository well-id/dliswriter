import re
from configparser import ConfigParser
from typing_extensions import Self
import logging
import importlib

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode, LogicalRecordType
from dlis_writer.logical_record.core.attribute.attribute import Attribute
from dlis_writer.logical_record.core.iflr_eflr_base import IflrAndEflrBase, IflrAndEflrRMeta
from dlis_writer.logical_record.core.logical_record import ConfigGenMixin


logger = logging.getLogger(__name__)


class EFLRMeta(IflrAndEflrRMeta):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj._instance_dict = {}
        return obj


class EFLR(IflrAndEflrBase, ConfigGenMixin, metaclass=EFLRMeta):
    """Represents an Explicitly Formatted Logical Record

    Attributes:
        name: Identifier of a Logical Record Segment. Must be
            distinct in a single Logical File.
        set_name: Optional identifier of the set a Logical Record Segment belongs to.

    """

    logical_record_type: LogicalRecordType
    is_eflr = True

    def __init__(self, name: str, set_name: str = None):
        super().__init__()

        self.name = name
        self.set_name = set_name

        self.origin_reference = None
        self.copy_number = 0

        self._instance_dict[name] = self

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

    def _make_set_component_bytes(self) -> bytes:
        """Creates component role Set

        Returns:
            Bytes that represent a Set component

        .._RP66 Component Descriptor:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_1
        """

        _bytes = write_struct(RepresentationCode.IDENT, self.set_type)
        if self.set_name:
            _bytes = b'\xf8' + _bytes + write_struct(RepresentationCode.IDENT, self.set_name)
        else:
            _bytes = b'\xf0' + _bytes

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

    def _make_obname_bytes(self) -> bytes:
        """Creates object component"""

        return b'p' + self.obname

    def _make_objects_bytes(self) -> bytes:
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

    def make_body_bytes(self) -> bytes:
        """Writes Logical Record Segment bytes without header"""

        set_component = self._make_set_component_bytes()
        template = self._make_template_bytes()
        obname = self._make_obname_bytes()
        objects = self._make_objects_bytes()

        return set_component + template + obname + objects

    @classmethod
    def make_lr_type_struct(cls, logical_record_type):
        return write_struct(RepresentationCode.USHORT, logical_record_type.value)

    def set_attributes(self, **kwargs):
        rep = f"{self.__class__.__name__} '{self.name}'"

        for attr_name, attr_value in kwargs.items():
            attr_name_main, *attr_parts = attr_name.split('.')
            attr_part = attr_parts[0] if attr_parts else 'value'
            if attr_part not in Attribute.settables:
                raise ValueError(f"Cannot set {attr_part} of an Attribute object")

            attr = getattr(self, attr_name_main, None)
            if not attr or not isinstance(attr, Attribute):
                logger.warning(f"{self.__class__.__name__} does not have attribute '{attr_name}'")

            logger.debug(f"Setting attribute '{attr_name}' of {rep} to {repr(attr_value)}")
            setattr(attr, attr_part, attr_value)

    @classmethod
    def get_or_make_all_from_config(cls, config: ConfigParser, keys: list[str] = None, key_pattern: str = None) -> list[Self]:
        if not keys:
            if key_pattern is None:
                key_pattern = cls.__name__ + r"-\w+"
            key_pattern = re.compile(key_pattern)
            keys = [key for key in config.sections() if key_pattern.fullmatch(key)]

        return [cls.get_or_make_from_config(key, config) for key in keys]
    
    @classmethod
    def get_instance(cls, name):
        return cls._instance_dict.get(name)

    @classmethod
    def get_all_instances(cls):
        return list(cls._instance_dict.values())

    @classmethod
    def clear_instances(cls):
        if cls._instance_dict:
            logger.debug(f"Removing all defined instances of {cls.__name__}")
            cls._instance_dict.clear()

    @classmethod
    def get_or_make_from_config(cls, name, config):
        if name in cls._instance_dict:
            return cls.get_instance(name)

        if name in config.sections():
            if (object_name := config[name].get('name', None)) in cls._instance_dict:
                return cls.get_instance(object_name)

        return cls.make_from_config(config, key=name)

    @classmethod
    def get_object_class(cls, object_name):
        module = importlib.import_module('dlis_writer.logical_record.eflr_types')

        class_name = object_name.split('-')[0]
        the_class = getattr(module, class_name, None)
        if the_class is None:
            raise ValueError(f"No EFLR class of name '{class_name}' found")

        return the_class

    def _make_lrb(self, bts, **kwargs):
        return super()._make_lrb(bts, is_eflr=True, **kwargs)

