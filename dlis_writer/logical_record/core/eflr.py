import re
from configparser import ConfigParser
from datetime import datetime
from typing_extensions import Self
import logging
import numpy as np

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.rp66 import RP66
from dlis_writer.utils.enums import RepresentationCode, LogicalRecordType
from dlis_writer.logical_record.core.attribute import Attribute
from dlis_writer.logical_record.core.iflr_eflr_base import IflrAndEflrBase


logger = logging.getLogger(__name__)


class EFLR(IflrAndEflrBase):
    """Represents an Explicitly Formatted Logical Record

    Attributes:
        object_name: Identifier of a Logical Record Segment. Must be
            distinct in a single Logical File.
        set_name: Optional identifier of the set a Logical Record Segment belongs to.

    """

    logical_record_type: LogicalRecordType
    is_eflr = True
    dtime_formats = ["%Y/%m/%d %H:%M:%S", "%Y.%m.%d %H:%M:%S"]

    def __init__(self, object_name: str, set_name: str = None):
        super().__init__()

        self.object_name = object_name
        self.set_name = set_name

        self.origin_reference = None
        self.copy_number = 0

        self._rp66_rules = getattr(RP66, self.set_type.replace('-', '_'))
        self._attributes: dict[str, Attribute] = {}

    def __str__(self):
        return f"{self.__class__.__name__} '{self.object_name}'"

    def __setattr__(self, key, value):
        if isinstance(getattr(self, key, None), Attribute):
            raise RuntimeError(f"Cannot set DLIS Attribute '{key}'. Did you mean setting '{key}.value' instead?")

        return super().__setattr__(key, value)

    def _create_attribute(self, key, **kwargs):
        rules = self._rp66_rules[key]

        attr = Attribute(
            label=key.strip('_').upper().replace('_', '-'),
            count=rules['count'],
            representation_code=rules['representation_code'],
            **kwargs
        )

        self._attributes[key] = attr

        return attr

    def get_attribute(self, name, fallback):
        return self._attributes.get(name, fallback)

    @property
    def obname(self) -> bytes:
        """Creates OBNAME bytes according to RP66 V1 spec

        Returns:
            OBNAME bytes that is used to identify an object in RP66 V1

        .._RP66 V1 OBNAME Representation Code:
            http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_23
        """

        return write_struct(
            RepresentationCode.OBNAME,
            (self.origin_reference, self.copy_number, self.object_name)
        )

    def make_set_component(self) -> bytes:
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

    def make_template(self) -> bytes:
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

    def make_object_component(self) -> bytes:
        """Creates object component"""

        return b'p' + self.obname

    def make_objects(self) -> bytes:
        """Creates object bytes that follows the object component

        Note:
            Each attribute of EFLR object is a logical_record.utils.core.Attribute instance
            Using Attribute instances' get_as_bytes method to create bytes.

        """

        _bytes = b''
        for attr in self._attributes.values():
            if not attr.value:
                _bytes += b'\x00'
            else:
                _bytes += attr.get_as_bytes()

        return _bytes

    def make_body_bytes(self) -> bytes:
        """Writes Logical Record Segment bytes without header"""

        a = self.make_set_component()
        b = self.make_template()
        c = self.make_objects()
        d = self.make_object_component()

        return a + b + d + c

    @classmethod
    def make_lr_type_struct(cls, logical_record_type):
        return write_struct(RepresentationCode.USHORT, logical_record_type.value)

    @staticmethod
    def convert_values(val, require_numeric=False):
        if isinstance(val, list):
            return val

        if isinstance(val, tuple):
            return list(val)

        if isinstance(val, np.ndarray):
            return val.tolist()

        if not isinstance(val, str):
            raise TypeError(f"Expected a list, tuple, np.ndarray, or str; got {type(val): val}")

        val = val.rstrip(' ').strip('[').rstrip(']')
        values = val.split(', ')
        values = [v.strip(' ').rstrip(' ') for v in values]

        for parser in (int, float):
            try:
                values = [parser(v) for v in values]
                break
            except ValueError:
                pass
        else:
            # if loop not broken - none of the converters worked
            if require_numeric:
                raise ValueError(f"Some/all of the values: {values} could not be converted to numeric types")
        return values

    @staticmethod
    def convert_dimension_or_el_limit(dim):
        err = TypeError(f"Expected a list/tuple of integers, a single integer, or a str parsable to list of integers; "
                        f"got {type(dim)}: {dim}")

        if not dim:
            raise err

        if isinstance(dim, (list, tuple)) and all(isinstance(v, int) for v in dim):
            return dim if isinstance(dim, list) else list(dim)

        if isinstance(dim, int):
            return [dim]

        if isinstance(dim, str):
            dim = dim.strip('[').rstrip(']')
            dim = dim.rstrip(' ').rstrip(',')
            try:
                return [int(v) for v in dim.split(', ')]
            except ValueError:
                raise err

        else:
            raise err

    @classmethod
    def parse_dtime(cls, dtime_string):
        if isinstance(dtime_string, datetime):
            return dtime_string

        if not isinstance(dtime_string, str):
            raise TypeError(f"Expected a str, got {type(dtime_string)}")

        for dtime_format in cls.dtime_formats:
            try:
                dtime = datetime.strptime(dtime_string, dtime_format)
            except ValueError:
                pass
            else:
                break
        else:
            # loop finished without breaking - no date format fitted to the string
            raise ValueError(f"Provided date time value does not conform to any of the allowed formats: "
                             f"{', '.join(fmt for fmt in cls.dtime_formats)}")

        return dtime

    def set_attributes(self, **kwargs):
        rep = f"{self.__class__.__name__} '{self.object_name}'"

        for attr_name, attr_value in kwargs.items():
            attr_name_main, *attr_parts = attr_name.split('.')
            attr_part = attr_parts[0] if attr_parts else 'value'
            if attr_part not in Attribute.settables:
                raise ValueError(f"Cannot set {attr_part} of an Attribute object")

            attr = self.get_attribute(attr_name_main, None)
            if not attr:
                logger.warning(f"{self.__class__.__name__} does not have attribute '{attr_name}'")

            logger.debug(f"Setting attribute '{attr_name}' of {rep} to {repr(attr_value)}")
            setattr(attr, attr_part, attr_value)

    def add_dependent_objects_from_config(self, config, attr_name, object_class, single=False):
        attr = getattr(self, attr_name)
        if attr.value is not None:
            if single:
                name = attr.value.rstrip(' ')
                attr.value = object_class.get_or_make_from_config(name, config)
            else:
                names_list = self.convert_values(attr.value)
                attr.value = [object_class.get_or_make_from_config(name, config) for name in names_list]

    @classmethod
    def all_from_config(cls, config: ConfigParser, keys: list[str] = None, key_pattern: str = None) -> list[Self]:
        if not keys:
            if key_pattern is None:
                key_pattern = cls.__name__ + r"-\w+"
            key_pattern = re.compile(key_pattern)
            keys = [key for key in config.sections() if key_pattern.fullmatch(key)]

        return [cls.from_config(config, key) for key in keys]
