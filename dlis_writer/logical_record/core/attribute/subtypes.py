import numpy as np
from .attribute import Attribute


class ListAttribute(Attribute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, multivalued=True, **kwargs)
        self._value_converter = self._converter
        self._converter = None

    @staticmethod
    def convert_values(val):
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
        values = self.convert_values(values)
        return [self._value_converter(v) for v in values]
