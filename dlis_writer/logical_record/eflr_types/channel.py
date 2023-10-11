import logging
import numpy as np

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import RepresentationCode, Units, LogicalRecordType


logger = logging.getLogger(__name__)


class Channel(EFLR):
    set_type = 'CHANNEL'
    logical_record_type = LogicalRecordType.CHANNL
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, object_name: str, set_name: str = None, dataset_name: str = None, **kwargs):

        super().__init__(object_name, set_name)

        self.long_name = self._create_attribute('long_name')
        self.properties = self._create_attribute('properties', converter=self.convert_properties)
        self.representation_code = self._create_attribute('representation_code', converter=self.convert_repr_code)
        self.units = self._create_attribute('units', converter=self.convert_unit)
        self.dimension = self._create_attribute('dimension', converter=self.convert_dimension_or_el_limit)
        self.axis = self._create_attribute('axis')
        self.element_limit = self._create_attribute('element_limit', converter=self.convert_dimension_or_el_limit)
        self.source = self._create_attribute('source')
        self.minimum_value = self._create_attribute('minimum_value', converter=float)
        self.maximum_value = self._create_attribute('maximum_value', converter=float)
        
        self.set_attributes(**kwargs)
        self._set_defaults()

        self._dataset_name: str = dataset_name

    @property
    def key(self):
        return hash(type(self)), self.object_name

    @property
    def name(self):
        return self.object_name

    @property
    def dataset_name(self):
        return self._dataset_name if self._dataset_name is not None else self.name

    @dataset_name.setter
    def dataset_name(self, name: str):
        self._dataset_name = name

    @staticmethod
    def convert_unit(unit):
        return Units.get_member(unit, allow_none=True)

    @staticmethod
    def convert_repr_code(rc):
        return RepresentationCode.get_member(rc, allow_none=True)

    @staticmethod
    def convert_dimension_or_el_limit(dim):
        err = TypeError(f"Expected a list/tuple of integers, a single integer, or a str parsable to list of integers; "
                        f"got {type(dim)}: {dim}")

        if not dim:
            raise err

        if isinstance(dim, (list, tuple)) and all(isinstance(v, int) for v in dim):
            return dim if isinstance(dim, list) else list(dim)

        if isinstance(dim, int):
            return [dim]

        if isinstance(dim, str):
            dim = dim.rstrip(' ').rstrip(',')
            try:
                return [int(v) for v in dim.split(', ')]
            except ValueError:
                raise err

        else:
            raise err

    @staticmethod
    def convert_properties(p):
        if isinstance(p, (list, tuple)) and all(isinstance(pp, str) for pp in p):
            return p if isinstance(p, list) else list(p)

        if isinstance(p, str):
            return p.split(", ")

        else:
            raise TypeError(f"Expected a str or a list/tuple of str, got {type(p)}: {p}")
        
    def set_dimension_from_data(self, data: np.ndarray):
        rep = f"Channel '{self.name}'"
        
        if self.dataset_name not in data.dtype.names:
            raise ValueError(f"No dataset with name '{self.dataset_name}' found in the data")
        
        dim = list(data[self.dataset_name].shape[1:]) or [1]

        if self.dimension.value != dim:
            if self.dimension.value:
                logger.warning(f"Previously defined dimension of {rep}: {self.dimension.value} "
                               f"does not match the dimension from data: {dim}")
            logger.debug(f"Setting dimension of {rep} to {dim}")
            self.dimension.value = dim

        if self.element_limit.value != dim:
            if self.element_limit.value:
                logger.warning(f"Previously defined element limit of {rep}: {self.element_limit.value} "
                               f"does not match the dimension from data: {dim}")
            logger.debug(f"Setting element limit of {rep} to {dim}")
            self.element_limit.value = dim

    def _set_defaults(self):
        
        if not self.element_limit.value and self.dimension.value:
            logger.debug(f"Setting element limit of channel '{self.name}' to the same value "
                         f"as dimension: {self.dimension.value}")
            self.element_limit.value = self.dimension.value
        elif not self.dimension.value and self.element_limit.value:
            logger.debug(f"Setting dimension of channel '{self.name}' to the same value "
                         f"as element limit: {self.element_limit.value}")
            self.dimension.value = self.element_limit.value
        elif self.element_limit.value != self.dimension.value:
            logger.warning(f"For channel '{self.name}', dimension is {self.dimension.value} "
                           f"and element limit is {self.element_limit.value}")

        if not self.long_name.value:
            logger.debug(f"Long name of channel '{self.name}' not specified; setting it to to the channel's name")
            self.long_name.value = self.name

        if not self.representation_code.value:
            rc = RepresentationCode.FDOUBL
            logger.debug(f"Representation code of channel '{self.name}' not specified; "
                         f"setting it to to {rc.name} ({rc.value})")
            self.representation_code.value = rc
