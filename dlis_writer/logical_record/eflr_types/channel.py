from typing import Union
from typing_extensions import Self
from configparser import ConfigParser
import logging

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
        self.properties = self._create_attribute('properties', converter=lambda p: p.split(", "))
        self.representation_code = self._create_attribute('representation_code',
                                                          converter=lambda v: RepresentationCode(int(v)))
        self.units = self._create_attribute('units', converter=Units.convert_unit)
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
    def convert_dimension_or_el_limit(dim):
        if isinstance(dim, list) and all(isinstance(v, int) for v in dim):
            return dim

        if isinstance(dim, int):
            return [dim]

        if isinstance(dim, str):
            dim = dim.rstrip(' ').rstrip(',')
            if not dim:
                return [1]
            return [int(v) for v in dim.split(', ')]

        else:
            raise TypeError("Expected a list of integers, a single integer, or a str parsable to list of integers; "
                            f"got {type(dim)}: {dim}")

    def _set_defaults(self):
        
        if not self.element_limit.value and self.dimension.value:
            logger.debug(f"Setting element limit of channel '{self.name}' to the same value "
                         f"as dimension: {self.dimension.value}")
            self.element_limit.value = self.dimension.value
        elif not self.dimension.value and self.element_limit.value:
            logger.debug(f"Setting dimension of channel '{self.name}' to the same value "
                         f"as element limit: {self.element_limit.value}")
            self.dimension.value = self.element_limit.value
        elif not self.element_limit.value and not self.dimension.value:
            logger.debug(f"Setting dimension and element limit of channel '{self.name}' to [1]")
            self.element_limit.value = [1]
            self.dimension.value = [1]
        else:
            if self.element_limit.value != self.dimension.value:
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
