from typing import Union, List, Tuple
import logging
import numpy as np

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode, Units, int_codes, float_codes, sint_codes, uint_codes
from dlis_writer.utils.converters import determine_repr_code


logger = logging.getLogger(__name__)


# custom type
AttributeValue = Union[int, float, str, List[int], List[float], List[str], Tuple[int], Tuple[float], Tuple[str]]


class Attribute:
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

    settables = ('representation_code', 'units', 'value')

    def __init__(self, label: str, multivalued: bool = False,
                 representation_code: RepresentationCode = None,
                 units: Units = None,
                 value: AttributeValue = None,
                 converter: callable = None
                 ):
        """Initiate Attribute object."""

        self._label = label.strip('_').upper().replace('_', '-')
        self._multivalued = multivalued
        self._representation_code = representation_code
        self._units = units
        self._value = value
        self._converter = converter  # to convert value from string retrieved from config file

    def __str__(self):
        return f"{self.__class__.__name__} '{self._label}'"

    @property
    def label(self):
        return self._label

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = self.convert_value(val)

    @property
    def representation_code(self):
        if self._representation_code is not None:
            return self._representation_code

        try:
            return self._guess_repr_code()
        except ValueError as exc:
            logger.warning(exc.args[0])
            return None

    def _guess_repr_code(self):
        if self._value is None:
            return None
        if self._multivalued:
            return self._guess_multivalued_repr_code()

        return determine_repr_code(self._value)

    def _guess_multivalued_repr_code(self):
        if not self._value:
            return None

        repr_codes = [determine_repr_code(v) for v in self._value]
        if len(set(repr_codes)) == 1:
            return repr_codes[0]

        if not all(rc in (float_codes + int_codes) for rc in repr_codes):
            logger.warning(f"Cannot determine a common representation code for values: {self._value} "
                           f"(proposed representation codes are: {repr_codes})")
            return None

        # at this stage we know all codes are numeric

        if any(all(rc in codes for rc in repr_codes) for codes in (float_codes, sint_codes, uint_codes)):
            # only floats, only signed ints, or only unsigned ints
            return max(repr_codes)

        if any(rc in float_codes for rc in repr_codes):
            # if any of them is a float - return the float code
            return max(rc for rc in repr_codes if rc in float_codes)

        if any(rc in sint_codes for rc in repr_codes):
            # if any of them is a signed int - return a signed int code
            max_uint_code = max(rc for rc in repr_codes if rc in uint_codes)
            max_sint_code = max(rc for rc in repr_codes if rc in sint_codes)
            if max_uint_code is RepresentationCode.ULONG:
                return max(RepresentationCode.SLONG, max_sint_code)
            if max_uint_code is RepresentationCode.UNORM:
                return max(RepresentationCode.SNORM, max_sint_code)
            return max_sint_code

        logger.warning(f"Cannot determine a representation code for values: {self._value}")
        return None

    @representation_code.setter
    def representation_code(self, rc):
        self._set_representation_code(rc)

    def _set_representation_code(self, rc):
        if self._representation_code is not None and self._representation_code is not rc:
            raise RuntimeError(f"representation code of {self} is already set to {self._representation_code.name}")
        self._representation_code = RepresentationCode.get_member(rc, allow_none=False)

    @property
    def units(self) -> Units:
        return self._units

    @units.setter
    def units(self, units: Union[str, Units]):
        self._units = Units.get_member(units, allow_none=True)

    @property
    def count(self) -> int:
        if not self._multivalued:
            return 1
        if self._value is None:
            return None
        if isinstance(self._value, (list, tuple)):
            return len(self._value)
        return 1

    @staticmethod
    def parse_values(val):
        if isinstance(val, list):
            values = val
        elif isinstance(val, tuple):
            values = list(val)
        elif isinstance(val, np.ndarray):
            values = val.tolist()
        elif isinstance(val, str):
            val = val.rstrip(' ').strip('[').rstrip(']').rstrip(',')
            values = val.split(', ')
            values = [v.strip(' ').rstrip(' ') for v in values]
        else:
            values = [val]

        return values

    def convert_value(self, value):
        if self._multivalued:
            value = self.parse_values(value)
            return [self.converter(v) for v in value]
        return self.converter(value)

    @property
    def converter(self):
        return self._converter or self.default_converter

    def default_converter(self, v):
        return v

    @converter.setter
    def converter(self, conv):
        if conv is None:
            self._converter = None
        else:
            if not callable(conv):
                raise TypeError(f"Expected a callable; got {type(conv)}")
            self._converter = conv

    def write_component_for_template(self, bts: bytes, characteristics: str) -> (bytes, str):
        """Write component of Attribute for template, as specified in RP66 V1."""

        if self._label:
            bts += write_struct(RepresentationCode.IDENT, self._label)
            characteristics += '1'
        else:
            characteristics += '0'

        characteristics += '0'

        if self.representation_code:
            bts += write_struct(RepresentationCode.USHORT, self.representation_code.value)
            characteristics += '1'
        else:
            characteristics += '0'

        if self._units:
            bts += write_struct(RepresentationCode.UNITS, self._units.value)
            characteristics += '1'
        else:
            characteristics += '0'

        return bts, characteristics

    def write_component_not_for_template(self, bts: bytes, characteristics: str) -> (bytes, str):
        """Write component of Attribute as specified in RP66 V1"""

        # label
        characteristics += '0'
        count = self.count

        if count and count != 1:
            bts += write_struct(RepresentationCode.UVARI, count)
            characteristics += '1'
        else:
            if self._value:
                if count is not None and count > 1:
                    bts += write_struct(RepresentationCode.UVARI, count)
                    characteristics += '1'
                else:
                    characteristics += '0'
            else:
                characteristics += '0'

        # representation code & units
        characteristics += '00'

        return bts, characteristics

    def write_values(self, bts: bytes, characteristics: str) -> (bytes, str):
        """Write value(s) passed to value attribute of this object."""

        rc = self.representation_code
        value = self._value

        if value:
            if isinstance(value, (list, tuple)):
                for val in value:
                    bts += write_struct(rc, val)
            else:
                if isinstance(value, Units):
                    value = value.value
                bts += write_struct(rc, value)

            characteristics += '1'

        else:
            characteristics += '0'

        return bts, characteristics

    def get_as_bytes(self, for_template=False) -> bytes:
        """Converts attribute object to bytes as specified in RP66 V1.

        Args:
            for_template: When True it creates the component only for the template part
                of Logical Record Segment in the DLIS file.

        Returns:
            Bytes that are compliant with the RP66 V1 spec

        """

        bts = b''
        characteristics = '001'

        if for_template:
            bts, characteristics = self.write_component_for_template(bts, characteristics)
            characteristics += '0'
        else:
            bts, characteristics = self.write_component_not_for_template(bts, characteristics)
            bts, characteristics = self.write_values(bts, characteristics)

        return write_struct(RepresentationCode.USHORT, int(characteristics, 2)) + bts

    @staticmethod
    def convert_numeric(value):
        for parser in (int, float):
            try:
                value = parser(value)
                break
            except ValueError:
                pass
        else:
            # if loop not broken - none of the converters worked
            raise ValueError(f"Some/all of the values: {value} could not be converted to numeric types")
        return value
