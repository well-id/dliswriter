import logging
from numbers import Number
from datetime import datetime
from typing import Union, Optional
from typing_extensions import Self
from configparser import ConfigParser

from .attribute import Attribute
from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject, EFLRMeta
from dlis_writer.utils.enums import RepresentationCode as RepC
from dlis_writer.utils.converters import ReprCodeConverter


logger = logging.getLogger(__name__)


class EFLRAttribute(Attribute):
    """Define an attribute whose value(s) is/are EFLRObject instances.

    Attributes like this are used when one EFLRObject instance points to another one - e.g. Zones of a Parameter
    or Channels of Frame.
    """

    def __init__(self, label: str, object_class: Optional[EFLRMeta] = None, representation_code: Optional[RepC] = None,
                 **kwargs):
        """Initialise EFLRAttribute.

        Args:
            label               :   Attribute label.
            object_class        :   EFLR subclass corresponding to the class of the object(s) - value of the attribute.
            representation_code :   Representation code to be used for the value. Can be OBNAME or OBJREF.
            kwargs              :   Keyword arguments passed to Attribute.
        """

        for arg_name in ('converter', 'units'):
            if kwargs.get(arg_name, None) is not None:
                raise TypeError(f"{self.__class__.__name__} does not accept '{arg_name}' argument")

        if representation_code is None:
            representation_code = RepC.OBNAME
        if representation_code not in (RepC.OBNAME, RepC.OBJREF):
            raise ValueError(f"Representation code '{representation_code.name}' is not allowed for an EFLRAttribute")

        if object_class is not None and not issubclass(object_class, EFLR):
            raise TypeError(f"Expected an EFLR subclass; got {object_class}")

        super().__init__(label=label, representation_code=representation_code, **kwargs)

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

    def finalise_from_config(self, config: ConfigParser):
        """Create EFLRObject instances from the earlier specified names.

        When an instance of the Attribute is created, the value might not be known yet.
        When setting up the attribute from config, initially only the name(s) of the ELFRObject(s) is/are known.
        These names are initially assigned to the self._value attribute.
        This method, using the config object from which the attribute itself was set up, sets up references to the
        correct EFLRObject instances based on the previously specified names.
        """

        if not self._value:
            logger.debug(f"No object names defined for {self}")
            return

        if self._multivalued:
            self._value = [self._make_eflr_object_from_config(config, v) for v in self._value]
        else:
            self._value = self._make_eflr_object_from_config(config, self._value)

    def _convert_value(self, v: Union[str, type]):
        """Implements default converter/checker for the value(s). Check that the value is a str or an EFLRObject."""

        object_class = self._object_class.object_type if self._object_class else EFLRObject
        if not isinstance(v, (object_class, str)):
            raise TypeError(f"Expected a str or instance of {object_class.__name__}; got {type(v)}: {v}")
        return v

    def _make_eflr_object_from_config(self, config: ConfigParser, object_name: Union[str, EFLRObject]) -> EFLRObject:
        """Create or retrieve an EFLRObject based on its name and the provided config object.

        If the value (object_name) is already an EFLRObject, return it as-is.
        """

        if isinstance(object_name, EFLRObject):
            return object_name

        if not isinstance(object_name, str):
            raise TypeError(f"Expected a str, got {type(object_name)}: {object_name}")

        object_class = self._object_class or EFLR.get_eflr_subclass(object_name)
        return object_class.make_object_from_config(config=config, key=object_name, get_if_exists=True)


class DTimeAttribute(Attribute):
    """Model an attribute whose value is a datetime object."""

    dtime_formats = ["%Y/%m/%d %H:%M:%S", "%Y.%m.%d %H:%M:%S"]  #: accepted date-time formats

    class DTimeFormatError(ValueError):
        """Error raised if a provided string does not match any of the allowed formats."""
        pass

    def __init__(self, *args, allow_float: bool = False, **kwargs):
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

    def __init__(self, *args, int_only: bool = False, float_only: bool = False, **kwargs):
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

    def copy(self):
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

    @property
    def representation_code(self) -> Union[RepC, None]:
        """Representation code of the attribute."""

        return super().representation_code

    @representation_code.setter
    def representation_code(self, rc: Union[RepC, str, int]):
        """Set a new representation code for the attribute. Check that the code refers to numerical values."""

        self._set_representation_code(rc)
        self._check_repr_code_numeric(self._representation_code)
        if self._value is not None:
            if self._multivalued:
                self._value = [self._convert_number(v) for v in self._value]
            else:
                self._value = self._convert_number(self._value)

    def _check_repr_code_numeric(self, rc: Union[RepC, None]):
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
    def _int_parser(value: Union[str, int, float]) -> int:
        """Parse a provided value as an integer."""

        if isinstance(value, str):
            value = int(value)  # ValueError possible, caught later if needed or allowed to propagate
        elif isinstance(value, Number):
            if not float(value).is_integer():
                raise ValueError(f"{value} cannot be represented as integer")
            value = int(value)
        else:
            raise TypeError(f"Cannot convert a {type(value)} object ({value}) to integer")
        return value

    @staticmethod
    def _float_parser(value: Union[str, int, float]) -> float:
        """Parse a provided value as a float."""

        if isinstance(value, str):
            value = float(value)  # ValueError possible
        elif isinstance(value, Number):
            value = float(value)
        else:
            raise TypeError(f"Cannot convert a {type(value)} object ({value}) to float")
        return value

    def _convert_number(self, value: Union[str, int, float]) -> Union[int, float]:
        """Convert a provided value according to the attribute's representation code (or as a float)."""

        rc = self._representation_code
        if rc is None:
            try:
                value = self._int_parser(value)
            except (ValueError, TypeError):
                value = self._float_parser(value)
            return value

        if rc in ReprCodeConverter.int_codes:
            return self._int_parser(value)

        if rc in ReprCodeConverter.float_codes:
            return self._float_parser(value)

        raise RuntimeError(f"Representation code {rc.name} is not numeric")


class DimensionAttribute(NumericAttribute):
    """Model an attribute expressing dimensions (e.g. dimension or element_limit of Channel)."""

    def __init__(self, *args, representation_code=RepC.UVARI, **kwargs):
        """Initialise a NumericAttribute.

        Args:
            args                :   Positional arguments passed to NumericAttribute.
            representation_code :   Representation code for the attribute value.
            kwargs              :   Keyword arguments passed to NumericAttribute.
        """

        if 'converter' in kwargs:
            raise TypeError(f"{self.__class__.__name__} does not accept 'converter' argument")

        super().__init__(*args, representation_code=representation_code, int_only=True, multivalued=True, **kwargs)

    def copy(self) -> Self:
        """Create a copy of the attribute instance."""

        return self.__class__(
            label=self._label,
            units=self._units,
            value=self._value,
        )

