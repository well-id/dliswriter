from abc import abstractmethod
from line_profiler_pycharm import profile
from typing import Union, List, Tuple

from .common import NOT_TEMPLATE
from .rp66 import RP66
from .common import write_struct
from .common import write_absent_attribute
from .converters import get_representation_code_value
from .converters import get_logical_record_type
from .enums import RepresentationCode
from .enums import Units


# custom type
AttributeValue = Union[int, float, str, List[int], List[float], List[str], Tuple[int], Tuple[float], Tuple[str]]


class Attribute(object):
    """Represents an RP66 V1 Attribute

    Attributes:
        label: String identifier to be used in Logical Record's template.
        count: The number of values in value attribute
        representation_code: One of the representation codes specified in RP66 V1 Appendix B
        units: Measurement units
        value: A single value or a list/tuple of values

    .._RP66 V1 Component Structure:
        http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2

    .._RP66 V1 Representation Codes:
        http://w3.energistics.org/rp66/v1/rp66v1_appb.html

    """

    def __init__(self, label: str, count: int=None,
                 representation_code: RepresentationCode=None,
                 units: str=None,
                 value: AttributeValue=None):
        """Initiates Attribute object"""
        
        self.label = label
        self.count = count
        self.representation_code = representation_code
        self.units = units
        self.value = value


    def write_component(self, for_template:bool):
        """Writes component of Attribute as specified in RP66 V1

        Args:
            for_template: When True it creates the component only for the template part
                of Logical Record Segment in the DLIS file.

        .._RP66 V1 Component Structure:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2

        """
        
        if self.label and for_template:
            self.bytes += write_struct(RepresentationCode.IDENT, self.label)
            self.characteristics += '1'
        else:
            self.characteristics += '0'


        if for_template:
            self.characteristics += '0'

        elif self.count and not for_template and self.count != 1:

            self.bytes += write_struct(RepresentationCode.UVARI, self.count)
            self.characteristics += '1'
        else:
            if self.value:
                if type(self.value) == list or type(self.value) == tuple:
                    self.count = len(self.value)
                else:
                    pass
                if self.count is not None and self.count > 1:
                    self.bytes += write_struct(RepresentationCode.UVARI, self.count)
                    self.characteristics += '1'
                else:
                    self.characteristics += '0'
            else:
                self.characteristics += '0'

        if self.representation_code and for_template:
            self.bytes += write_struct(RepresentationCode.USHORT, get_representation_code_value(self.representation_code))
            self.characteristics += '1'
        else:
            self.characteristics += '0'

        if self.units and for_template:
            if type(self.units) == Units:
                self.bytes += write_struct(RepresentationCode.UNITS, self.units.value)
            else:
                self.bytes += write_struct(RepresentationCode.UNITS, self.units)
            self.characteristics += '1'
        else:
            self.characteristics += '0'


    def write_values(self, for_template:bool):
        """Writes value(s) passed to value attribute of this object

        Args:
            for_template: When True it creates the component only for the template part
                of Logical Record Segment in the DLIS file.

        .._RP66 V1 Component Structure:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2
        """

        if self.value and not for_template:
            
            if type(self.value) == list or type(self.value) == tuple:
                for val in self.value:
                    if 'logical_record' in str(type(val)):
                        self.bytes += val.obname
                    else:
                        self.bytes += write_struct(self.representation_code, val)
            else:
                try:
                    if type(self.value) == Units:
                        value = self.value.value
                    else:
                        value = self.value

                    self.bytes += write_struct(self.representation_code, value)
                except:
                    raise Exception(f'{self.representation_code} ----- {self.value}')

            self.characteristics += '1'

        else:
            self.characteristics += '0'

            
    def write_characteristics(self, for_template:bool):
        """Writes component descriptor as specified in RP66 V1

        Args:
            for_template: When True it creates the component only for the template part
                of Logical Record Segment in the DLIS file.

        .._RP66 V1 Component Descriptor:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_1
        """
        self.bytes = write_struct(RepresentationCode.USHORT, int(self.characteristics, 2)) + self.bytes


    def get_as_bytes(self, for_template=False) -> bytes:
        """Converts attribute object to bytes as specified in RP66 V1.

        Args:
            for_template: When True it creates the component only for the template part
                of Logical Record Segment in the DLIS file.

        Returns:
            Bytes that are compliant with the RP66 V1 spec

        """        
        self.bytes = b''
        self.characteristics = '001'
        
        self.write_component(for_template)
        self.write_values(for_template)
        self.write_characteristics(for_template)

        return self.bytes


class EFLR(object):
    """Represents an Explicitly Formatted Logical Record

    Attributes:
        object_name: Identifier of a Logical Record Segment. Must be
            distinct in a single Logical File.
        set_name: Optional identifier of the set a Logical Record Segment belongs to. 

    """

    def __init__(self, object_name:str, set_name:str=None, *args, **kwargs):

        self.object_name = object_name
        self.set_name = set_name
        
        self.origin_reference = None
        self.copy_number = 0

        self.segment_length = None
        self.logical_record_type = None
        
        self.is_eflr = True
        self.has_predecessor_segment = False
        self.has_successor_segment = False
        self.is_encrypted = False
        self.has_encryption_protocol = False
        self.has_checksum = False
        self.has_trailing_length = False
        self.has_padding = False


        self.set_type = None

        self.is_dictionary_controlled = False
        self.dictionary_controlled_objects = None


    def create_attributes(self):
        """Creates Attribute instances for each attribute in the __dict__ except NO_TEMPLATE elements"""
        for key in list(self.__dict__.keys()):
            if key not in NOT_TEMPLATE:
                _rules = getattr(RP66, self.set_type.replace('-','_'))[key]

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
    def segment_attributes(self) -> bytes:
        """Writes the logical record segment attributes.

        .._RP66 V1 Logical Record Segment Header:
            http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1

        """
        _bits = str(int(self.is_eflr))\
                + str(int(self.has_predecessor_segment))\
                + str(int(self.has_successor_segment))\
                + str(int(self.is_encrypted))\
                + str(int(self.has_encryption_protocol))\
                + str(int(self.has_checksum))\
                + str(int(self.has_trailing_length))\
                + str(int(self.has_padding))

        return write_struct(RepresentationCode.USHORT, int(_bits, 2))

    @property
    def header_bytes(self) -> bytes:
        """Writes Logical Record Segment Header

        .._RP66 V1 Logical Record Segment Header:
            http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1

        """
        self.segment_length = len(self.bytes) + 4
        if self.segment_length % 2 != 0:
            self.segment_length += 1
            self.has_padding = True
        else:
            self.has_padding = False

        return write_struct(RepresentationCode.UNORM, self.segment_length)\
               + self.segment_attributes\
               + write_struct(RepresentationCode.USHORT, get_logical_record_type(self.logical_record_type))

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

    @property
    def size(self) -> bytes:
        """Calculates the size of the Logical Record Segment"""
        try:
            return len(self.represent_as_bytes())
        except:
            raise Exception(f'\n\n{self}\n\n')

    @property
    def padding_bytes(self) -> bytes:
        """Writes padding bytes"""
        return write_struct(RepresentationCode.USHORT, 1)

    @profile
    def represent_as_bytes(self):
        """Writes bytes of the entire Logical Record Segment that is an EFLR object"""
        
        self.bytes = b''
        self.bytes += self.body_bytes
        self.bytes = self.header_bytes + self.bytes
        if self.has_padding:
            self.bytes += self.padding_bytes

        return self.bytes

    def split(self, is_first:bool, is_last:bool, segment_length:int, add_extra_padding:bool) -> bytes:
        """Creates header bytes to be inserted into split position
        
        When a Logical Record Segment overflows a Visible Record, it must be split.
        A split operation involves:
            1. Changing the header of the first part of the split
            2. Adding a header to the second part of the split

        Args:
            is_first: Represents whether this is the first part of the split
            is_last: Represents whether this is the last part of the split
            segment_length: Length of the segment after split operation
            add_extra_padding: If after the split the segment length is smaller than 16
                adds extra padding to comply with the minimum length.

        Returns:
            Header bytes to be inserted into split position

        """

        assert int(is_first) + int(is_last) != 2, 'Split segment can not be both FIRST and LAST'
        assert segment_length % 2 == 0, 'Split segment length is not an EVEN NUMBER'
        assert segment_length < self.size, 'Split segment length can not be larger than the whole segment'

        _length = write_struct(RepresentationCode.UNORM, segment_length)

        toggle_padding = False
        
        if is_first:
            self.has_predecessor_segment = False
        else:
            self.has_predecessor_segment = True

        if is_last:
            self.has_successor_segment = False
        else:
            self.has_successor_segment = True
            if self.has_padding is not add_extra_padding:
                toggle_padding = True
                self.has_padding = not self.has_padding

        _attributes = self.segment_attributes

        if toggle_padding:
            self.has_padding = not self.has_padding

        return _length + _attributes + write_struct(RepresentationCode.USHORT, get_logical_record_type(self.logical_record_type))

    def __repr__(self):
        """String representation of this object"""
        return self.set_type


# class DictionaryControlledObject:
#     """Obsolete class"""
#
#     def __init__(self, object_name:str, *args, **kwargs):
#
#         self.origin_reference = None
#         self.copy_number = 0
#         self.object_name = object_name
#
#     @property
#     def obname(self):
#         return write_struct(RepresentationCode.OBNAME, (self.origin_reference,
#                                                         self.copy_number,
#                                                         self.object_name))
#
#     def create_attributes(self):
#         for key in list(self.__dict__.keys()):
#             if key not in NOT_TEMPLATE:
#                 _rules = getattr(RP66, self.set_type.replace('-','_'))[key]
#
#                 _label = key.upper().replace('_', '-')
#                 _count = _rules['count']
#                 _rc = _rules['representation_code']
#
#                 _attr = Attribute(label=_label, count=_count, representation_code=_rc)
#                 setattr(self, key, _attr)
#
#     def write_obname(self):
#         self.bytes += b'p'
#         self.bytes += self.obname
#
#     def write_attributes(self):
#         for key in list(self.__dict__.keys()):
#             if key not in NOT_TEMPLATE:
#                 _attr = getattr(self, key)
#                 if not _attr.value:
#                     self.bytes += write_absent_attribute()
#                 else:
#                     self.bytes += _attr.get_as_bytes()
#
#     @property
#     def as_bytes(self):
#         self.bytes = b''
#         self.write_obname()
#         self.write_attributes()
#
#         return self.bytes


class IFLR(object):
    """Similar to EFLR object with is_eflr=False

    Methods docstrings are not added as they are the same with EFLR.
    """
    def __init__(self):


        self.logical_record_type = None
        self.iflr_type = None
        
        self.is_eflr = False
        self.has_predecessor_segment = False
        self.has_successor_segment = False
        self.is_encrypted = False
        self.has_encryption_protocol = False
        self.has_checksum = False
        self.has_trailing_length = False
        self.has_padding = False

    @property
    @abstractmethod
    def body_bytes(self):
        pass

    @property
    def segment_attributes(self) -> bytes:

        _bits = f'{int(self.is_eflr)}' \
                f'{int(self.has_predecessor_segment)}' \
                f'{int(self.has_successor_segment)}' \
                f'{int(self.is_encrypted)}' \
                f'{int(self.has_encryption_protocol)}' \
                f'{int(self.has_checksum)}' \
                f'{int(self.has_trailing_length)}' \
                f'{int(self.has_padding)}'

        return write_struct(RepresentationCode.USHORT, int(_bits, 2))

    @property
    def size(self):
        return len(self.represent_as_bytes())

    @property
    def header_bytes(self) -> bytes:
        self.segment_length = len(self.body_bytes) + 4
        if self.segment_length % 2 != 0:
            self.segment_length += 1
            self.has_padding = True
        else:
            self.has_padding = False

        return write_struct(RepresentationCode.UNORM, self.segment_length)\
               + self.segment_attributes\
               + write_struct(RepresentationCode.USHORT, self.iflr_type)

    @profile
    def represent_as_bytes(self):
        _bytes = self.body_bytes # Create 
        _bytes = self.header_bytes + _bytes
        if self.has_padding:
            _bytes += write_struct(RepresentationCode.USHORT, 1) # Padding

        return _bytes

    def split(self, is_first:bool, is_last:bool, segment_length:int, add_extra_padding:bool) -> bytes:
        """Returns header bytes to be inserted into split position(s)"""

        assert int(is_first) + int(is_last) != 2, 'Splitted segment can not be both FIRST and LAST'
        assert segment_length % 2 == 0, 'Splitted segment length is not an EVEN NUMBER'
        assert segment_length < self.size, 'Splitted segment length can not be larger than the whole segment'

        _length = write_struct(RepresentationCode.UNORM, segment_length)

        toggle_padding = False
        
        if is_first:
            self.has_predecessor_segment = False
        else:
            self.has_predecessor_segment = True

        if is_last:
            self.has_successor_segment = False
        else:
            self.has_successor_segment = True
            if self.has_padding is not add_extra_padding:
                toggle_padding = True
                self.has_padding = not self.has_padding

        _attributes = self.segment_attributes

        if toggle_padding:
            self.has_padding = not self.has_padding

        return _length + _attributes + write_struct(RepresentationCode.USHORT, self.iflr_type)

    def __repr__(self):
        return self.set_type