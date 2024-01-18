import logging
from numbers import Number
from datetime import datetime
from typing import Union, Optional, Any
from typing_extensions import Self

from .attribute import Attribute
from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem, EFLRSetMeta
from dlis_writer.utils.enums import RepresentationCode as RepC
from dlis_writer.utils.converters import ReprCodeConverter


logger = logging.getLogger(__name__)


class EFLRAttribute(Attribute):
    """Define an attribute whose value(s) is/are EFLRObject instances.

    Attributes like this are used when one EFLRObject instance points to another one - e.g. Zones of a Parameter
    or Channels of Frame.
    """

    _units_settable = False
    _valid_repr_codes = (RepC.OBNAME, RepC.OBJREF)
    _default_repr_code = RepC.OBNAME

    def __init__(self, label: str, object_class: Optional[EFLRSetMeta] = None, **kwargs: Any) -> None:
        """Initialise EFLRAttribute.

        Args:
            label               :   Attribute label.
            object_class        :   EFLR subclass corresponding to the class of the object(s) - value of the attribute.
            kwargs              :   Keyword arguments passed to Attribute.
        """

        for arg_name in ('converter', 'units'):
            if kwargs.get(arg_name, None) is not None:
                raise TypeError(f"{self.__class__.__name__} does not accept '{arg_name}' argument")

        if object_class is not None and not issubclass(object_class, EFLRSet):
            raise TypeError(f"Expected an EFLR subclass; got {object_class}")

        super().__init__(label=label, **kwargs)

        self._object_class = object_class
        self._converter = self._convert_value

    def copy(self) -> Self:
        """Create a copy of the attribute instance."""

        return self.__class__(
            label=self._label,
            multivalued=self._multivalued,
            representation_code=self._representation_code,
            value=self._value,
            object_class=self._object_class
        )

    def _convert_value(self, v: type[EFLRItem]) -> type[EFLRItem]:
        """Implements default converter/checker for the value(s). Check that the value is an EFLRObject."""

        object_class = self._object_class.item_type if self._object_class else EFLRItem
        if not isinstance(v, object_class):
            raise TypeError(f"Expected an instance of {object_class.__name__}; got {type(v)}: {v}")
        return v


class DTimeAttribute(Attribute):
    """Model an attribute whose value is a datetime object."""

    dtime_formats = ["%Y/%m/%d %H:%M:%S", "%Y.%m.%d %H:%M:%S"]  #: accepted date-time formats
    _valid_repr_codes = (RepC.DTIME, RepC.FDOUBL, RepC.FSINGL)

    class DTimeFormatError(ValueError):
        """Error raised if a provided string does not match any of the allowed formats."""
        pass

    def __init__(self, *args: Any, allow_float: bool = False, **kwargs: Any) -> None:
        """Initialise a DTimeAttribute.

        Args:
            args        :   Positional arguments passed to Attribute.
            allow_float :   If True, allow for the value to be a float (e.g. a number of seconds since a specific
                            vent). Otherwise, raise an error if the user attempts to set float as the value.
            kwargs      :   Keyword arguments passed to Attribute.
        """

        super().__init__(*args, **kwargs)

        if allow_float and kwargs.get('representation_code', None) is RepC.DTIME:
            raise ValueError("Representation code cannot be specified as DTIME if float time format is allowed")

        self._allow_float = allow_float
        if not self._allow_float and not self._representation_code:
            self._representation_code = RepC.DTIME
        if not self._converter:
            self._converter = self._convert_value

    def _convert_value(self, value: Union[str, datetime, int, float]) -> Union[datetime, float]:
        """Default value converter: parse string as date time or (if so specified at init) as a float."""

        if isinstance(value, datetime):
            return value

        if isinstance(value, Number) and self._allow_float:
            return float(value)

        if not isinstance(value, str):
            raise TypeError(f"Expected a datetime object, number, or str; got {type(value)}: {value}")

        try:
            return self.parse_dtime(value)
        except self.DTimeFormatError as exc:
            if self._allow_float:
                return float(value)
            else:
                raise exc

    @classmethod
    def parse_dtime(cls, dtime_string: str) -> datetime:
        """Parse a string to a datetime object if it matches any of the allowed formats."""

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
            raise cls.DTimeFormatError(f"Provided date time value does not conform to any of the allowed formats: "
                                       f"{', '.join(fmt for fmt in cls.dtime_formats)}")

        return dtime


class NumericAttribute(Attribute):
    """Model an attribute which can only have numerical values."""

    _valid_repr_codes = ReprCodeConverter.numeric_codes

    def __init__(self, *args: Any, int_only: bool = False, float_only: bool = False, **kwargs: Any) -> None:
        """Initialise a NumericAttribute.

        Args:
            args        :   Positional arguments passed to Attribute.
            int_only    :   If True, allow only integer values.
            float_only  :   If True, allow only float values (not integers).
            kwargs      :   Keyword arguments passed to Attribute.
        """

        self._int_only = int_only
        self._float_only = float_only

        if self._int_only and self._float_only:
            raise ValueError("'int_only' and 'float_only' cannot both be True")

        if rc := kwargs.get('representation_code', None):
            self._check_repr_code_numeric(rc)

        super().__init__(*args, **kwargs)
        if not self._converter:
            self._converter = self._convert_number

    def copy(self) -> Self:
        """Create a copy of the attribute instance."""

        return self.__class__(
            label=self._label,
            multivalued=self._multivalued,
            representation_code=self._representation_code,
            units=self._units,
            value=self._value,
            converter=self._converter,
            int_only=self._int_only,
            float_only=self._float_only
        )

    def _check_repr_code_numeric(self, rc: Union[RepC, None]) -> None:
        """Check that the provided representation code, if not None, is of appropriate numerical type."""

        if rc is None:
            return

        if self._int_only and rc not in ReprCodeConverter.int_codes:
            raise ValueError(f"Representation code {rc.name} is not integer")

        if self._float_only and rc not in ReprCodeConverter.float_codes:
            raise ValueError(f"Representation code {rc.name} is not float")

        if rc not in ReprCodeConverter.numeric_codes:
            raise ValueError(f"Representation code {rc.name} is not numeric")

    @staticmethod
    def _int_parser(value: Number) -> int:
        """Parse a provided value as an integer."""

        if not isinstance(value, Number):
            raise TypeError(f"Cannot convert a {type(value)} object ({value}) to integer")

        if not float(value).is_integer():
            raise ValueError(f"{value} cannot be represented as integer")

        return int(value)

    @staticmethod
    def _float_parser(value: Number) -> float:
        """Parse a provided value as a float."""

        if not isinstance(value, Number):
            raise TypeError(f"Cannot convert a {type(value)} object ({value}) to float")

        return float(value)

    def _convert_number(self, value: Number) -> Union[int, float]:
        """Convert a provided value according to the attribute's representation code (or as a float)."""

        if self._int_only or self.representation_code in ReprCodeConverter.int_codes:
            return self._int_parser(value)

        return self._float_parser(value)


class DimensionAttribute(NumericAttribute):
    """Model an attribute expressing dimensions (e.g. dimension or element_limit of Channel)."""

    _units_settable = False
    _valid_repr_codes = (RepC.UVARI,)
    _default_repr_code = RepC.UVARI

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise a NumericAttribute.

        Args:
            args                :   Positional arguments passed to NumericAttribute.
            kwargs              :   Keyword arguments passed to NumericAttribute.
        """

        if 'converter' in kwargs:
            raise TypeError(f"{self.__class__.__name__} does not accept 'converter' argument")

        super().__init__(*args, int_only=True, multivalued=True, **kwargs)

    def copy(self) -> Self:
        """Create a copy of the attribute instance."""

        return self.__class__(
            label=self._label,
            units=self._units,
            value=self._value,
        )


class StatusAttribute(Attribute):
    """Model an attribute which can only have value 1 or 0."""

    _units_settable = False
    _valid_repr_codes = (RepC.STATUS,)
    _default_repr_code = RepC.STATUS

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise a StatusAttribute.

        Args:
            args        :   Positional arguments passed to Attribute.
            kwargs      :   Keyword arguments passed to Attribute.
        """

        super().__init__(*args, **kwargs, converter=self.convert_status)

    @staticmethod
    def convert_status(val: Union[bool, int, float]) -> int:
        """Convert a provided value to 1 or 0."""

        if isinstance(val, bool):
            return int(val)

        if isinstance(val, float) and val % 1:
            raise ValueError(f"Status cannot be a fraction; got {val}")

        val = int(val)
        if val not in (0, 1):
            raise ValueError(f"Status must be a 1 or a 0; got {val}")

        return val

    def copy(self) -> Self:
        """Create a copy of the attribute instance."""

        return self.__class__(
            label=self._label,
            multivalued=self._multivalued,
            value=self._value
        )


class TextAttribute(Attribute):
    """Model an attribute representing text in ASCII format."""

    _units_settable = False
    _valid_repr_codes = (RepC.ASCII,)
    _default_repr_code = RepC.ASCII

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise an ASCIIAttribute.

        Args:
            args        :   Positional arguments passed to Attribute.
            kwargs      :   Keyword arguments passed to Attribute.
        """

        super().__init__(*args, **kwargs, converter=self._check_string)

    @staticmethod
    def _check_string(v: str) -> str:
        if not isinstance(v, str):
            raise TypeError(f'Expected a str, got {type(v)}: {v}')
        return v

    def copy(self) -> Self:
        """Create a copy of the attribute instance."""

        return self.__class__(
            label=self._label,
            multivalued=self._multivalued,
            value=self._value
        )


class IdentAttribute(Attribute):
    """Model an attribute represented as IDENT."""

    _units_settable = False
    _valid_repr_codes = (RepC.IDENT,)
    _default_repr_code = RepC.IDENT

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise an IDENTAttribute.

        Args:
            args        :   Positional arguments passed to Attribute.
            kwargs      :   Keyword arguments passed to Attribute.
        """

        super().__init__(*args, **kwargs)

    def copy(self) -> Self:
        """Create a copy of the attribute instance."""

        return self.__class__(
            label=self._label,
            multivalued=self._multivalued,
            value=self._value
        )

