import logging
from numbers import Number
from datetime import datetime

from .attribute import Attribute
from dlis_writer.logical_record.core.eflr import EFLR
from dlis_writer.utils.enums import RepresentationCode as RepC
from dlis_writer.utils.converters import ReprCodeConverter


logger = logging.getLogger(__name__)


class EFLRAttribute(Attribute):
    def __init__(self, *args, object_class=None, representation_code=RepC.OBNAME, **kwargs):
        if 'converter' in kwargs:
            raise TypeError(f"{self.__class__.__name__} does not accept 'converter' argument")

        super().__init__(*args, representation_code=representation_code, **kwargs)

        self._object_class = object_class
        self._converter = self._convert_value

    def copy(self):
        return self.__class__(
            label=self._label,
            multivalued=self._multivalued,
            representation_code=self._representation_code,
            units=self._units,
            value=self._value,
            object_class=self._object_class
        )

    def finalise_from_config(self, config):
        if not self._value:
            logger.warning(f"No object names defined for {self}")
            return

        if self._multivalued:
            self._value = [self._make_eflr_object_from_config(config, v) for v in self._value]
        else:
            self._value = self._make_eflr_object_from_config(config, self._value)

    def _convert_value(self, v):
        object_class = self._object_class or EFLR
        if not isinstance(v, (object_class, str)):
            raise TypeError(f"Expected a str or instance of {object_class.__name__}; got {type(v)}: {v}")
        return v

    def _make_eflr_object_from_config(self, config, object_name):
        if isinstance(object_name, EFLR):
            return object_name

        if not isinstance(object_name, str):
            raise TypeError(f"Expected a str, got {type(object_name)}: {object_name}")

        object_class = self._object_class or EFLR.get_eflr_subclass(object_name)
        return object_class.make_object_from_config(config, object_name, get_if_exists=True)


class DTimeAttribute(Attribute):
    dtime_formats = ["%Y/%m/%d %H:%M:%S", "%Y.%m.%d %H:%M:%S"]

    class DTimeFormatError(ValueError):
        pass

    def __init__(self, *args, allow_float=False, **kwargs):
        super().__init__(*args, **kwargs)

        if allow_float and kwargs.get('representation_code', None) is RepC.DTIME:
            raise ValueError("Representation code cannot be specified as DTIME if float time format is allowed")

        self._allow_float = allow_float
        if not self._allow_float and not self._representation_code:
            self._representation_code = RepC.DTIME
        if not self._converter:
            self._converter = self._convert_value

    def _convert_value(self, value):
        try:
            value = self.parse_dtime(value)
        except self.DTimeFormatError as exc:
            if self._allow_float:
                value = float(value)
            else:
                raise exc

        return value

    @classmethod
    def parse_dtime(cls, dtime_string):
        if isinstance(dtime_string, datetime):
            return dtime_string

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
    def __init__(self, *args, int_only=False, float_only=False, **kwargs):
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
    def representation_code(self):
        return super().representation_code

    @representation_code.setter
    def representation_code(self, rc):
        self._set_representation_code(rc)
        self._check_repr_code_numeric(self._representation_code)
        if self._value is not None:
            if self._multivalued:
                self._value = [self._convert_number(v) for v in self._value]
            else:
                self._value = self._convert_number(self._value)

    def _check_repr_code_numeric(self, rc):
        if self._int_only and rc not in ReprCodeConverter.int_codes:
            raise ValueError(f"Representation code {rc.name} is not integer")

        if self._float_only and rc not in ReprCodeConverter.float_codes:
            raise ValueError(f"Representation code {rc.name} is not float")

        if rc not in ReprCodeConverter.numeric_codes:
            raise ValueError(f"Representation code {rc.name} is not numeric")

    @staticmethod
    def _int_parser(value):
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
    def _float_parser(value):
        if isinstance(value, str):
            value = float(value)  # ValueError possible
        elif isinstance(value, Number):
            value = float(value)
        else:
            raise TypeError(f"Cannot convert a {type(value)} object ({value}) to float")
        return value

    def _convert_number(self, value):
        rc = self._representation_code
        if not self._representation_code:
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
    def __init__(self, *args, representation_code=RepC.UVARI, **kwargs):
        if 'converter' in kwargs:
            raise TypeError(f"{self.__class__.__name__} does not accept 'converter' argument")

        super().__init__(*args, representation_code=representation_code, int_only=True, multivalued=True, **kwargs)

    def copy(self):
        return self.__class__(
            label=self._label,
            units=self._units,
            value=self._value,
        )

