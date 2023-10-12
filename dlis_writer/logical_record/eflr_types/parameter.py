from configparser import ConfigParser

import numpy as np
from typing_extensions import Self

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Parameter(EFLR):
    set_type = 'PARAMETER'
    logical_record_type = LogicalRecordType.STATIC
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.long_name = self._create_attribute('long_name')
        self.dimension = self._create_attribute('dimension', converter=self.convert_dimension_or_el_limit)
        self.axis = self._create_attribute('axis')
        self.zones = self._create_attribute('zones')
        self.values = self._create_attribute('values', converter=self.convert_values)

        self.set_attributes(**kwargs)

    @staticmethod
    def convert_values(val):
        if isinstance(val, list):
            return val

        if isinstance(val, tuple):
            return list(val)

        if isinstance(val, np.ndarray):
            return val.tolist()

        if not isinstance(val, str):
            raise TypeError(f"Expected a list, tuple, np.ndarray, or str; got {type(val): val}")

        val = val.rstrip(' ').strip('[').rstrip(']')
        values = val.split(', ')
        values = [v.strip(' ').rstrip(' ') for v in values]

        for parser in (int, float):
            try:
                values = [parser(v) for v in values]
                return values
            except ValueError:
                pass
        return values

    @classmethod
    def from_config(cls, config: ConfigParser, key=None, add_zones=True) -> Self:
        obj: Self = super().from_config(config, key=key)

        # TODO: add zones

        return obj

