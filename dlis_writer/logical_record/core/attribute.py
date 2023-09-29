from typing import Union, List, Tuple

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.converters import get_representation_code_value
from dlis_writer.utils.enums import RepresentationCode, Units

from line_profiler_pycharm import profile


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

    def __init__(self, label: str, count: int = None,
                 representation_code: RepresentationCode = None,
                 units: Units = None,
                 value: AttributeValue = None):
        """Initiate Attribute object."""

        self.label = label
        self.count = count
        self.representation_code = representation_code
        self._units = units
        self.value = value

    @property
    def units(self) -> Units:
        return self._units

    @units.setter
    def units(self, units: Union[str, Units]):

        if not isinstance(units, Units):
            units = Units[units]

        self._units = units

    def write_component_for_template(self, bts: bytes, characteristics: str) -> (bytes, str):
        """Write component of Attribute for template, as specified in RP66 V1."""

        if self.label:
            bts += write_struct(RepresentationCode.IDENT, self.label)
            characteristics += '1'
        else:
            characteristics += '0'

        characteristics += '0'

        if self.representation_code:
            bts += write_struct(RepresentationCode.USHORT, get_representation_code_value(self.representation_code))
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

        if self.count and self.count != 1:
            bts += write_struct(RepresentationCode.UVARI, self.count)
            characteristics += '1'
        else:
            if self.value:
                if isinstance(self.value, (list, tuple)):
                    self.count = len(self.value)

                if self.count is not None and self.count > 1:
                    bts += write_struct(RepresentationCode.UVARI, self.count)
                    characteristics += '1'
                else:
                    characteristics += '0'
            else:
                characteristics += '0'

        # representation code & units
        characteristics += '00'

        return bts, characteristics

    @profile
    def write_values(self, bts: bytes, characteristics: str) -> (bytes, str):
        """Write value(s) passed to value attribute of this object."""

        if self.value:
            if isinstance(self.value, (list, tuple)):
                for val in self.value:
                    bts += write_struct(self.representation_code, val)
            else:
                value = self.value.value if isinstance(self.value, Units) else self.value
                bts += write_struct(self.representation_code, value)

            characteristics += '1'

        else:
            characteristics += '0'

        return bts, characteristics

    @profile
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
