import numpy as np
import logging
from numbers import Number
from datetime import datetime

from .attribute import Attribute
from dlis_writer.logical_record.core.eflr import EFLR
from dlis_writer.utils.enums import RepresentationCode as RepC
from dlis_writer.utils.converters import determine_repr_code


logger = logging.getLogger(__name__)


class ListAttribute(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, multivalued=True, **kwargs)
        self._value_converter = self._converter or (lambda v: v)
        self._converter = None

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

    def default_converter(self, values):
        values = self.parse_values(values)
        return [self._value_converter(v) for v in values]

    def _guess_repr_code(self):
        if not self._value:
            return None

        return determine_repr_code(self._value[0])


class _EFLRAttributeMixin:
    def __init__(self, *args, object_class=None, representation_code=RepC.OBNAME, **kwargs):
        if 'converter' in kwargs:
            raise TypeError(f"{self.__class__.__name__} does not accept 'converter' argument")

        super().__init__(*args, representation_code=representation_code, **kwargs)
        self._object_class = object_class

    def _convert_value(self, v):
        object_class = self._object_class or EFLR
        if not isinstance(v, (object_class, str)):
            raise TypeError(f"Expected a str or instance of {object_class.__name__}; got {type(v)}: {v}")
        return v

    def _make_eflr_object_from_config(self, config, object_name):
        if not isinstance(object_name, str):
            raise TypeError(f"Expected a str, got {type(object_name)}: {object_name}")
        object_class = self._object_class or EFLR.get_object_class(object_name)
        return object_class.get_or_make_from_config(object_name, config)


class EFLRListAttribute(_EFLRAttributeMixin, ListAttribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value_converter = self._convert_value

    def finalise_from_config(self, config):
        if not self._value:
            logger.warning(f"No object names defined for {self}")
            return

        objects = []
        for i, v in enumerate(self._value):
            if isinstance(self._value, EFLR):
                logger.info(f"Value {i} of {self} is already an instance of EFLR")
                objects.append(v)
            else:
                objects.append(self._make_eflr_object_from_config(config, v))

        self._value = objects


class EFLRAttribute(_EFLRAttributeMixin, Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._converter = self._convert_value

    def finalise_from_config(self, config):
        if not self._value:
            logger.warning(f"No object name defined for {self}")
            return
        if isinstance(self._value, EFLR):
            logger.info(f"Value of {self} is already an instance of EFLR")
        self._value = self._make_eflr_object_from_config(config, self._value)


class DimensionAttribute(ListAttribute):
    def __init__(self, *args, representation_code=RepC.UVARI, **kwargs):
        if 'converter' in kwargs:
            raise TypeError(f"{self.__class__.__name__} does not accept 'converter' argument")

        super().__init__(*args, representation_code=representation_code, **kwargs)
        self._value_converter = self.convert_integer

    @staticmethod
    def convert_integer(value):
        if isinstance(value, str):
            return int(value)
        if isinstance(value, Number):
            if value % 1:
                raise ValueError(f"{value} is not an integer")
            return int(value)
        else:
            raise TypeError(f"Cannot convert {type(value)}: {value} to integer")


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
