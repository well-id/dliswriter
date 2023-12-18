from typing import Union, Any, TYPE_CHECKING, Callable, Optional
from typing_extensions import Self
import logging

from dlis_writer.utils.struct_writer import write_struct, write_struct_ascii, write_struct_uvari
from dlis_writer.utils.enums import RepresentationCode, UNITS
from dlis_writer.utils.converters import ReprCodeConverter

if TYPE_CHECKING:
    from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem


logger = logging.getLogger(__name__)


class Attribute:
    """Represent an RP66 V1 Attribute."""

    settables = ('representation_code', 'units', 'value')  #: attributes of the object which can be set

    def __init__(self, label: str, multivalued: bool = False, representation_code: Optional[RepresentationCode] = None,
                 units: Optional[str] = None, value: Any = None, converter: Optional[Callable] = None,
                 parent_eflr: "Optional[Union[EFLRSet, EFLRItem]]" = None):
        """Initialise an Attribute object.

        Args:
            label               :   Name of the attribute. Leading underscores are removed, other underscores
                                    are swapped for dashes. The letters are transformed to uppercase.
            multivalued         :   True if the attribute is allowed to have multiple values.
            representation_code :   Representation code for the attribute value (or each of its values
                                    in 'multivalued' case).
            units               :   Unit the value(s) is/are expressed in.
            value               :   Value(s) of the attribute.
            converter           :   Function used to convert/validate the provided value later, through the 'value'
                                    property setter.
            parent_eflr         :   EFLR or EFLRObject instance this attribute belongs to.

        """

        self._check_type(label, str)
        self._check_type(multivalued, bool)
        self._check_type(representation_code, RepresentationCode, allow_none=True)
        self._check_type(units, str, allow_none=True)

        if converter and not callable(converter):
            raise TypeError(f"Converter must be a callable; got {type(converter)}: {converter}")

        self._label = label.strip('_').upper().replace('_', '-')
        self._multivalued = multivalued
        self._representation_code = representation_code
        self._units = units
        self._value = value
        self._converter = converter  # to convert value
        self._parent_eflr = parent_eflr

    @staticmethod
    def _check_type(value: Any, *expected_types: type, allow_none: bool = False):
        """Check that value is an instance of the expected type. If not, raise a TypeError."""

        if allow_none and value is None:
            return

        if not isinstance(value, expected_types):
            tp = '/'.join(t.__name__ for t in expected_types)
            raise TypeError(f"Expected an instance of {tp}; got {type(value)}: {value}")

    def __str__(self) -> str:
        """String representation of the attribute."""

        return f"{self.__class__.__name__} '{self._label}'" + (f' of {self._parent_eflr}' if self._parent_eflr else '')

    @property
    def label(self) -> str:
        """Label of the attribute to be used in the created file."""

        return self._label

    @property
    def value(self) -> Any:
        """Value of the attribute."""

        return self._value

    @value.setter
    def value(self, val: Any):
        """Set a new value of the attribute. Use the provided converter (if any) to transform/validate the value."""

        self._value = self.convert_value(val)

    @property
    def representation_code(self) -> Union[RepresentationCode, None]:
        """Representation code of the attribute; explicitly assigned if available, otherwise guessed from the value."""

        return self.assigned_representation_code or self.inferred_representation_code

    @representation_code.setter
    def representation_code(self, rc: Union[RepresentationCode, str, int]):
        """Set a new representation code for the attribute."""

        self._set_representation_code(rc)

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

        try:
            return ReprCodeConverter.determine_repr_code_from_value(self._value)
        except ReprCodeConverter.ReprCodeError as exc:
            logger.warning(exc.args[0])
            return None

    @property
    def assigned_representation_code(self) -> Union[RepresentationCode, None]:
        """Explicitly assigned representation code of the attribute."""

        return self._representation_code

    @property
    def inferred_representation_code(self) -> Union[RepresentationCode, None]:
        """Representation code guessed from the attribute value (if possible)."""

        return self._guess_repr_code()

    def _set_representation_code(self, rc: Union[RepresentationCode, str, int]):
        """Set representation code, having checked that no (other) representation code has previously been set.

        This check is implemented because it is assumed that if a representation code is assigned at init, it is the
        only allowed representation code for this attribute and should not be changed. If multiple options for a
        representation code of a given attribute exist, the value is not set at init and can be changed later.
        """

        self._check_type(rc, RepresentationCode, str, int)
        rcm = RepresentationCode.get_member(rc, allow_none=False)

        if self._representation_code is not None and self._representation_code is not rcm:
            raise RuntimeError(f"representation code of {self} is already set to {self._representation_code.name}")
        self._representation_code = rcm

    @property
    def units(self) -> Union[str, None]:
        """Unit of the attribute value(s)."""

        return self._units

    @units.setter
    def units(self, units: str):
        """Set new units for the attribute."""

        if units is not None:
            self._check_type(units, str)
            if units not in UNITS:
                logger.warning(f"'{units}' is not among the units allowed by the standard")
        self._units = units

    @property
    def count(self) -> Union[int, None]:
        """Return number of values of the attribute or None if value is not set (is None)."""

        if not self._multivalued:
            return 1
        if self._value is None:
            return None
        if isinstance(self._value, (list, tuple)):
            return len(self._value)
        return 1

    @property
    def parent_eflr(self) -> "Union[EFLRSet, EFLRItem, None]":
        """EFLR or ELFRObject instance the attribute belongs to."""

        return self._parent_eflr

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

        return self._converter or (lambda v: v)

    @converter.setter
    def converter(self, conv: Union[Callable, None]):
        """Set a new converter for the attribute (or remove an existing one by passing 'None')."""

        if conv is None:
            self._converter = None
        else:
            if not callable(conv):
                raise TypeError(f"Expected a callable; got {type(conv)}")
            self._converter = conv

    def _write_for_template(self, bts: bytes, characteristics: str) -> tuple[bytes, str]:
        """Transform the attribute to bytes and characteristics needed for an EFLR template."""

        if self._label:
            bts += write_struct_ascii(self._label)
            characteristics += '1'
        else:
            characteristics += '0'

        # count, representation code, units, and value - no defaults
        characteristics += '0000'

        return bts, characteristics

    def _write_for_body(self, bts: bytes, characteristics: str) -> tuple[bytes, str]:
        """Transform the attribute to bytes anf characteristics needed to describe this part of an EFLRObject."""

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

    def _write_values(self, bts: bytes, characteristics: str) -> tuple[bytes, str]:
        """Transform the attribute to bytes and characteristics for template/describing its EFLRObject."""

        rc = self.representation_code
        value = self._value

        if value is not None:
            if isinstance(value, (list, tuple)):
                for val in value:
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
            for_template: If True, create the bytes for EFLR template; otherwise, for EFLRObject description.
        """

        bts = b''
        characteristics = '001'

        if for_template:
            bts, characteristics = self._write_for_template(bts, characteristics)
        else:
            bts, characteristics = self._write_for_body(bts, characteristics)

        return RepresentationCode.USHORT.convert(int(characteristics, 2)) + bts

    def copy(self) -> Self:
        """Create a copy of the attribute instance; do not include parent_eflr reference."""

        return self.__class__(
            label=self._label,
            multivalued=self._multivalued,
            representation_code=self._representation_code,
            units=self._units,
            value=self._value,
            converter=self._converter,
        )
