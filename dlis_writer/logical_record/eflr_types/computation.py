import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.eflr_types.tool import Tool
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.utils.enums import LogicalRecordType


logger = logging.getLogger(__name__)


class Computation(EFLR):
    set_type = 'COMPUTATION'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        super().__init__(object_name, set_name)

        self.long_name = self._create_attribute('long_name')
        self.properties = self._create_attribute('properties', converter=self.convert_values)
        self.dimension = self._create_attribute('dimension', converter=self.convert_dimension_or_el_limit)
        self.axis = self._create_attribute('axis')
        self.zones = self._create_attribute('zones')
        self.values = self._create_attribute(
            'values', converter=lambda val: self.convert_values(val, require_numeric=True))
        self.source = self._create_attribute('source')

        self.set_attributes(**kwargs)
        self._set_defaults()

    def _set_defaults(self):
        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]

    @classmethod
    def from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'zones', Zone)
        obj.add_dependent_objects_from_config(config, 'axis', Axis, single=True)
        obj.add_dependent_objects_from_config(config, 'source', Tool, single=True)

        return obj

