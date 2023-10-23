from configparser import ConfigParser
from typing_extensions import Self
import logging

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType
from dlis_writer.logical_record.eflr_types.zone import Zone


logger = logging.getLogger(__name__)


class Parameter(EFLR):
    set_type = 'PARAMETER'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.long_name = self._create_attribute('long_name')
        self.dimension = self._create_attribute('dimension', converter=self.convert_dimension_or_el_limit)
        self.axis = self._create_attribute('axis')
        self.zones = self._create_attribute('zones')
        self.values = self._create_attribute('values', converter=self.convert_values)

        self.set_attributes(**kwargs)
        self._set_defaults()

    def _set_defaults(self):
        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'zones', Zone)

        return obj

