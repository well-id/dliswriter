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

    def __init__(self, *args, dataset_name: str = None, **kwargs):

        super().__init__(*args, **kwargs)

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
            return [int(v) for v in dim.split(', ')]

        else:
            raise TypeError("Expected a list of integers, a single integer, or a str parsable to list of integers; "
                            f"got {type(dim)}: {dim}")

    @classmethod
    def create(cls, name: str, dimension: int = 1, long_name: str = None, repr_code: RepresentationCode = None,
               unit: Union[Units, str] = None, element_limit: int = None, dataset_name: str = None) -> Self:
        """

        Args:
            name:
            dimension:

            long_name:
            repr_code:
            unit:
            element_limit:

        Returns:
            channel:
        """

        channel = Channel(name)
        channel.long_name.value = long_name or name
        channel.representation_code.value = (repr_code if repr_code is not None else RepresentationCode.FDOUBL)
        channel.dimension.value = [dimension]
        channel.element_limit.value = [element_limit if element_limit is not None else dimension]

        channel.dataset_name = dataset_name

        if unit is not None:
            channel.units.value = unit

        return channel

    @classmethod
    def from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().from_config(config, key=key)

        key = key or cls.__name__
        if 'dataset_name' in config[key].keys():
            obj.dataset_name = config[key]['dataset_name']

        if not obj.element_limit.value and obj.dimension.value:
            logger.debug(f"Setting element limit of channel '{obj.name}' to the same value "
                         f"as dimension: {obj.dimension.value}")
            obj.element_limit.value = obj.dimension.value
        elif not obj.dimension.value and obj.element_limit.value:
            logger.debug(f"Setting dimension of channel '{obj.name}' to the same value "
                         f"as element limit: {obj.element_limit.value}")
            obj.dimension.value = obj.element_limit.value
        elif not obj.element_limit.value and not obj.dimension.value:
            logger.debug(f"Setting dimension and element limit of channel '{obj.name}' to [1]")
            obj.element_limit.value = [1]
            obj.dimension.value = [1]
        else:
            if obj.element_limit.value != obj.dimension.value:
                logger.warning(f"For channel '{obj.name}', dimension is {obj.dimension.value} "
                               f"and element limit is {obj.element_limit.value}")

        if not obj.long_name.value:
            logger.debug(f"Long name of channel '{obj.name}' not specified; setting it to to the channel's name")
            obj.long_name.value = obj.name

        if not obj.representation_code.value:
            rc = RepresentationCode.FDOUBL
            logger.debug(f"Representation code of channel '{obj.name}' not specified; "
                         f"setting it to to {rc.name} ({rc.value})")
            obj.representation_code.value = rc

        return obj
