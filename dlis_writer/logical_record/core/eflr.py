from dlis_writer.utils.common import NOT_TEMPLATE, write_struct, write_absent_attribute
from dlis_writer.utils.rp66 import RP66
from dlis_writer.utils.converters import get_logical_record_type
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.attribute import Attribute
from dlis_writer.logical_record.core.iflr_eflr_base import IflrAndEflrBase


class EFLR(IflrAndEflrBase):
    """Represents an Explicitly Formatted Logical Record

    Attributes:
        object_name: Identifier of a Logical Record Segment. Must be
            distinct in a single Logical File.
        set_name: Optional identifier of the set a Logical Record Segment belongs to.

    """

    is_eflr = True
    logical_record_type: str = NotImplemented

    def __init__(self, object_name: str, set_name: str = None, *args, **kwargs):
        super().__init__()

        self.object_name = object_name
        self.set_name = set_name

        self.origin_reference = None
        self.copy_number = 0

        self.is_dictionary_controlled = False
        self.dictionary_controlled_objects = None

    def create_attributes(self):
        """Creates Attribute instances for each attribute in the __dict__ except NO_TEMPLATE elements"""
        for key in list(self.__dict__.keys()):
            if key not in NOT_TEMPLATE:
                _rules = getattr(RP66, self.set_type.replace('-', '_'))[key]

                if key[0] == '_':
                    _label = key[1:].upper().replace('_', '-')
                else:
                    _label = key.upper().replace('_', '-')

                _count = _rules['count']
                _rc = _rules['representation_code']

                _attr = Attribute(label=_label, count=_count, representation_code=_rc)
                setattr(self, key, _attr)

    @property
    def obname(self) -> bytes:
        """Creates OBNAME bytes according to RP66 V1 spec

        Returns:
            OBNAME bytes that is used to identify an object in RP66 V1

        .._RP66 V1 OBNAME Representation Code:
            http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_23
        """
        return write_struct(RepresentationCode.OBNAME, (self.origin_reference,
                                                        self.copy_number,
                                                        self.object_name))

    @property
    def set_component(self) -> bytes:
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

    @property
    def template(self) -> bytes:
        """Creates template from EFLR object's attributes

        Returns:
            Template bytes compliant with the RP66 V1

        .._RP66 V1 Component Usage:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_2

        """
        _bytes = b''
        for key in list(self.__dict__.keys()):
            if key not in NOT_TEMPLATE:
                _attr = getattr(self, key)
                _bytes += _attr.get_as_bytes(for_template=True)

        return _bytes

    @property
    def object_component(self) -> bytes:
        """Creates object component"""
        _bytes = b'p'
        _bytes += self.obname

        return _bytes

    @property
    def objects(self) -> bytes:
        """Creates object bytes that follows the object component

        Note:
            Each attribute of EFLR object is a logical_record.utils.core.Attribute instance
            Using Attribute instances' get_as_bytes method to create bytes.

        """
        _bytes = b''
        if self.is_dictionary_controlled:
            for obj in self.dictionary_controlled_objects:
                _bytes += obj.represent_as_bytes()
        else:
            for key in list(self.__dict__.keys()):
                if key not in NOT_TEMPLATE:
                    _attr = getattr(self, key)
                    if not _attr.value:
                        _bytes += write_absent_attribute()
                    else:
                        _bytes += _attr.get_as_bytes()

        return _bytes

    @property
    def header_bytes(self) -> bytes:
        """Writes Logical Record Segment Header

        .._RP66 V1 Logical Record Segment Header:
            http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1

        """
        segment_length = len(self.bytes) + 4
        if segment_length % 2 != 0:
            segment_length += 1
            self.has_padding = True
        else:
            self.has_padding = False

        return write_struct(RepresentationCode.UNORM, segment_length) \
            + self.segment_attributes \
            + self._write_struct_for_lr_type()

    @property
    def body_bytes(self) -> bytes:
        """Writes Logical Record Segment bytes without header"""
        if self.is_dictionary_controlled:
            a = self.set_component
            b = self.template
            c = self.objects
            return a + b + c
        else:
            a = self.set_component
            b = self.template
            d = self.object_component
            c = self.objects
            return a + b + d + c

    def _write_struct_for_lr_type(self):
        return write_struct(RepresentationCode.USHORT, get_logical_record_type(self.logical_record_type))
