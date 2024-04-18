from typing import Union, Any, TYPE_CHECKING, Callable, Optional
import logging

from dliswriter.utils.internal.struct_writer import write_struct, write_struct_ascii, write_struct_uvari
from dliswriter.utils.internal.internal_enums import RepresentationCode
from dliswriter.utils.enums import Unit
from dliswriter.utils.internal.converters import ReprCodeConverter

if TYPE_CHECKING:
    from dliswriter.logical_record.core.eflr import EFLRItem


logger = logging.getLogger(__name__)


class Attribute:
    """Represent an RP66 V1 Attribute."""

    _valid_repr_codes = tuple(RepresentationCode.__members__.values())
    _default_repr_code: Union[RepresentationCode, None] = None
    _units_settable: bool = True

    def __init__(self, label: str, multivalued: bool = False, multidimensional: bool = False,
                 representation_code: Optional[RepresentationCode] = None, units: Optional[str] = None,
                 value: Any = None, converter: Optional[Callable] = None, parent_eflr: "Optional[EFLRItem]" = None):
        """Initialise an Attribute object.

        Args:
            label               :   Name of the attribute. Leading underscores are removed, other underscores
                                    are swapped for dashes. The letters are transformed to uppercase.
            multivalued         :   True if the attribute is allowed to have multiple values.
            multidimensional    :   True if the attribute is allowed to have multiple dimensions - e.g. nested lists
                                    - as values.
            representation_code :   Representation code for the attribute value (or each of its values
                                    in 'multivalued' case).
            units               :   Unit the value(s) is/are expressed in.
            value               :   Value(s) of the attribute.
            converter           :   Function used to convert/validate the provided value later, through the 'value'
                                    property setter.
            parent_eflr         :   EFLRSet or EFLRItem instance this attribute belongs to.

        """

        self._check_type(label, str)
        self._check_type(multivalued, bool)
        self._check_type(multidimensional, bool)
        self._check_type(representation_code, RepresentationCode, allow_none=True)
        self._check_type(units, str, allow_none=True)

        if multidimensional and not multivalued:
            raise ValueError("An Attribute cannot be multidimensional without being multivalued")

        if converter and not callable(converter):
            raise TypeError(f"Converter must be a callable; got {type(converter)}: {converter}")

        self._label = label.strip('_').upper().replace('_', '-')
        self._multivalued = multivalued
        self._multidimensional = multidimensional
        self._representation_code = representation_code if representation_code is not None else self._default_repr_code
        self._units = units
        self._value = value
        self._converter = converter  # to convert value
        self.parent_eflr = parent_eflr

        self._unit_checker = Unit.make_converter("units", soft=True, allow_none=True)

    @staticmethod
    def _check_type(value: Any, *expected_types: type, allow_none: bool = False) -> None:
        """Check that value is an instance of the expected type. If not, raise a TypeError."""

        if allow_none and value is None:
            return

        if not isinstance(value, expected_types):
            tp = '/'.join(t.__name__ for t in expected_types)
            raise TypeError(f"Expected an instance of {tp}; got {type(value)}: {value}")

    def __str__(self) -> str:
        """String representation of the attribute."""

        return f"{self.__class__.__name__} '{self._label}'" + (f' of {self.parent_eflr}' if self.parent_eflr else '')

    @property
    def label(self) -> str:
        """Label of the attribute to be used in the created file."""

        return self._label

    @property
    def value(self) -> Any:
        """Value of the attribute."""

        return self._value

    @value.setter
    def value(self, val: Any) -> None:
        """Set a new value of the attribute. Use the provided converter (if any) to transform/validate the value."""

        self._value = self.convert_value(val)

    @property
    def representation_code(self) -> Union[RepresentationCode, None]:
        """Representation code of the attribute; explicitly assigned if available, otherwise guessed from the value."""

        return self._representation_code or self.inferred_representation_code

    def _guess_repr_code(self) -> Union[RepresentationCode, None]:
        """Attempt determining representation code of the attribute from the set value.

        Returns None if:
            - value is not set (is None)
            - in multivalued case: value is an empty iterable
            - no representation code corresponding to the set value(s) could be found.
        """

        if self._value is None:
            return None
        if self._multivalued:
            if not self._value:
                return None

        value_flat = self.flatten_list(self._value) if self._multidimensional else self._value

        try:
            return ReprCodeConverter.determine_repr_code_from_value(value_flat)
        except ReprCodeConverter.ReprCodeError as exc:
            logger.warning(exc.args[0])
            return None

    @property
    def inferred_representation_code(self) -> Union[RepresentationCode, None]:
        """Representation code guessed from the attribute value (if possible)."""

        rc = self._guess_repr_code()

        if rc is not None and rc not in self._valid_repr_codes:
            raise RuntimeError(f"Value {repr(self._value)} is not of valid type "
                               f"for attribute type {self.__class__.__name__}")

        return rc

    @property
    def units(self) -> Union[str, None]:
        """Unit of the attribute value(s)."""

        return self._units

    @units.setter
    def units(self, units: str) -> None:
        """Set new units for the attribute."""

        if not self._units_settable:
            raise RuntimeError(f"Units of {self.__class__.__name__} cannot be set")

        self._unit_checker(units)
        self._units = units

    @property
    def count(self) -> Union[int, None]:
        """Return number of values of the attribute or None if value is not set (is None)."""

        if not self._multivalued:
            return 1
        if self._value is None:
            return None
        if isinstance(self._value, (list, tuple)):
            return len(self.flatten_list(self._value))
        return 1

    @property
    def multivalued(self) -> bool:
        """True if multiple values (list of values) can be added; False otherwise."""

        return self._multivalued

    @property
    def multidimensional(self) -> bool:
        """True if attribute's value can have multiple dimensions (e.g. nested lists). False otherwise."""

        return self._multidimensional

    def convert_value(self, value: Any) -> Any:
        """Transform/validate the provided value according to the provided converter.

        If the attribute is set up as multivalued, before converting the value, parse it to a list."""

        if self._multivalued:
            if not isinstance(value, (list, tuple)):
                value = [value]
            return [self.converter(v) for v in value]
        return self.converter(value)

    @property
    def converter(self) -> Callable:
        """Converter used to transform/validate values set through the setter of property 'value'."""

        conv = self._converter or (lambda v: v)

        def wrapper(value: Any) -> Any:
            if self._multidimensional and isinstance(value, (list, tuple)):
                return [wrapper(value_element) for value_element in value]
            return conv(value)

        return wrapper

    @converter.setter
    def converter(self, conv: Union[Callable, None]) -> None:
        """Set a new converter for the attribute (or remove an existing one by passing 'None')."""

        if conv is None:
            self._converter = None
        else:
            if not callable(conv):
                raise TypeError(f"Expected a callable; got {type(conv)}")
            self._converter = conv

    def _write_for_template(self, bts: bytes, characteristics: str) -> tuple[bytes, str]:
        """Transform the attribute to bytes and characteristics needed for an EFLRSet template."""

        if self._label:
            bts += write_struct_ascii(self._label)
            characteristics += '1'
        else:
            characteristics += '0'

        # count, representation code, units, and value - no defaults
        characteristics += '0000'

        return bts, characteristics

    def _write_for_body(self, bts: bytes, characteristics: str) -> tuple[bytes, str]:
        """Transform the attribute to bytes and characteristics needed to describe this part of an EFLRItem."""

        # label
        characteristics += '0'

        # count
        count = self.count
        if count and count != 1:
            bts += write_struct_uvari(count)
            characteristics += '1'
        else:
            if self._value is not None:
                if count is not None and count > 1:
                    bts += write_struct_uvari(count)
                    characteristics += '1'
                else:
                    characteristics += '0'
            else:
                characteristics += '0'

        # representation code
        if self.representation_code:
            bts += RepresentationCode.USHORT.convert(self.representation_code.value)
            characteristics += '1'
        else:
            characteristics += '0'

        # units
        if self._units:
            bts += write_struct_ascii(self._units)
            characteristics += '1'
        else:
            characteristics += '0'

        # values
        bts, characteristics = self._write_values(bts, characteristics)

        return bts, characteristics

    @staticmethod
    def flatten_list(v: Union[list, tuple], res: Optional[list] = None) -> list:
        """Take a possibly nested list or tuple and produce a flat list."""

        if res is None:
            res = []

        for vv in v:
            if isinstance(vv, (list, tuple)):
                res = Attribute.flatten_list(vv, res)
            else:
                res.append(vv)

        return res

    def _write_values(self, bts: bytes, characteristics: str) -> tuple[bytes, str]:
        """Transform the attribute to bytes and characteristics for template/describing its EFLRItem."""

        rc = self.representation_code
        value = self._value

        if value is not None:
            if isinstance(value, (list, tuple)):
                for val in self.flatten_list(value):
                    bts += write_struct(rc, val)
            else:
                bts += write_struct(rc, value)

            characteristics += '1'

        else:
            characteristics += '0'

        return bts, characteristics

    def get_as_bytes(self, for_template: bool = False) -> bytes:
        """Convert attribute to bytes to be put in the DLIS file.

        Args:
            for_template: If True, create the bytes for EFLRSet template; otherwise, for EFLRItem description.
        """

        bts = b''
        characteristics = '001'

        if for_template:
            bts, characteristics = self._write_for_template(bts, characteristics)
        else:
            bts, characteristics = self._write_for_body(bts, characteristics)

        return RepresentationCode.USHORT.convert(int(characteristics, 2)) + bts
