from configparser import ConfigParser
from typing_extensions import Self
import logging

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

    is_eflr = True
    logical_record_type: LogicalRecordType = NotImplemented

    def __init__(self, object_name: str, set_name: str = None):
        super().__init__()

        self.object_name = object_name
        self.set_name = set_name

        self.origin_reference = None
        self.copy_number = 0

        self._rp66_rules = getattr(RP66, self.set_type.replace('-', '_'))
        self._attributes: dict[str, Attribute] = {}

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

    @classmethod
    def from_config(cls, config: ConfigParser) -> Self:

        obj: Self = super().from_config(config)
        key = cls.__name__

        if (attributes_key := f"{key}.attributes") not in config.sections():
            logger.info(f"No attributes of {key} defined in the config")
            return obj

        for attr_name, attr_value in config[attributes_key].items():
            attr_name_main, *attr_parts = attr_name.split('.')
            attr_part = attr_parts[0] if attr_parts else 'value'
            if attr_part not in Attribute.settables:
                raise ValueError(f"Cannot set {attr_part} of an Attribute object")

            attr = obj.get_attribute(attr_name_main, None)
            if not attr:
                logger.warning(f"{key} does not have attribute '{attr_name}'")

            logger.debug(f"Setting attribute '{attr_name}' of {key} to {repr(attr_value)}")
            setattr(attr, attr_part, attr_value)

        return obj
