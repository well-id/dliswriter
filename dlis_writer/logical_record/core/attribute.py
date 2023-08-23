from typing import Union, List, Tuple

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.converters import get_representation_code_value
from dlis_writer.utils.enums import RepresentationCode, Units


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
                 units: str = None,
                 value: AttributeValue = None):
        """Initiates Attribute object"""

        self.label = label
        self.count = count
        self.representation_code = representation_code
        self.units = units
        self.value = value

    def write_component(self, for_template: bool, bts: bytes, characteristics: str) -> (bytes, str):
        """Writes component of Attribute as specified in RP66 V1

        Args:
            for_template: When True it creates the component only for the template part
                of Logical Record Segment in the DLIS file.
            bts: TODO
            characteristics: TODO

        .._RP66 V1 Component Structure:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2

        """

        if self.label and for_template:
            bts += write_struct(RepresentationCode.IDENT, self.label)
            characteristics += '1'
        else:
            characteristics += '0'

        if for_template:
            characteristics += '0'

        elif self.count and not for_template and self.count != 1:

            bts += write_struct(RepresentationCode.UVARI, self.count)
            characteristics += '1'
        else:
            if self.value:
                if type(self.value) == list or type(self.value) == tuple:
                    self.count = len(self.value)
                else:
                    pass
                if self.count is not None and self.count > 1:
                    bts += write_struct(RepresentationCode.UVARI, self.count)
                    characteristics += '1'
                else:
                    characteristics += '0'
            else:
                characteristics += '0'

        if self.representation_code and for_template:
            bts += write_struct(RepresentationCode.USHORT, get_representation_code_value(self.representation_code))
            characteristics += '1'
        else:
            characteristics += '0'

        if self.units and for_template:
            if type(self.units) == Units:
                bts += write_struct(RepresentationCode.UNITS, self.units.value)
            else:
                bts += write_struct(RepresentationCode.UNITS, self.units)
            characteristics += '1'
        else:
            characteristics += '0'

        return bts, characteristics

    def write_values(self, for_template: bool, bts: bytes, characteristics: str) -> (bytes, str):
        """Writes value(s) passed to value attribute of this object

        Args:
            for_template: When True it creates the component only for the template part
                of Logical Record Segment in the DLIS file.
            bts: TODO
            characteristics: TODO

        .._RP66 V1 Component Structure:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2
        """

        if self.value and not for_template:

            if type(self.value) == list or type(self.value) == tuple:
                for val in self.value:
                    if 'logical_record' in str(type(val)):
                        bts += val.obname
                    else:
                        bts += write_struct(self.representation_code, val)
            else:
                try:
                    if type(self.value) == Units:
                        value = self.value.value
                    else:
                        value = self.value

                    bts += write_struct(self.representation_code, value)
                except:
                    raise Exception(f'{self.representation_code} ----- {self.value}')

            characteristics += '1'

        else:
            characteristics += '0'

        return bts, characteristics

    def write_characteristics(self, for_template: bool, bts: bytes, characteristics: str) -> bytes:
        """Writes component descriptor as specified in RP66 V1

        Args:
            for_template: When True it creates the component only for the template part
                of Logical Record Segment in the DLIS file.
            bts: TODO
            characteristics: TODO

        .._RP66 V1 Component Descriptor:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_1
        """

        bts = write_struct(RepresentationCode.USHORT, int(characteristics, 2)) + bts
        return bts

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

        bts, characteristics = self.write_component(for_template, bts, characteristics)
        bts, characteristics = self.write_values(for_template, bts, characteristics)
        bts = self.write_characteristics(for_template, bts, characteristics)

        return bts
