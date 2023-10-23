import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


logger = logging.getLogger(__name__)


class Computation(EFLR):
    set_type = 'COMPUTATION'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.long_name = self._create_attribute('long_name', representation_code=RepC.ASCII)
        self.properties = self._create_attribute(
            'properties', converter=self.convert_values, multivalued=True, representation_code=RepC.IDENT)
        self.dimension = self._create_attribute(
            'dimension', converter=self.convert_dimension_or_el_limit,
            multivalued=True, representation_code=RepC.UVARI)
        self.axis = self._create_attribute('axis', multivalued=True, representation_code=RepC.OBNAME)
        self.zones = self._create_attribute('zones', multivalued=True, representation_code=RepC.OBNAME)
        self.values = self._create_attribute(
            'values', converter=lambda val: self.convert_values(val, require_numeric=True), multivalued=True)
        self.source = self._create_attribute('source', multivalued=True)

        self.set_attributes(**kwargs)
        self._set_defaults()

    def _set_defaults(self):
        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]

    def check_values_and_zones(self):
        if self.values.value is not None and self.zones.value is not None:
            if (nv := len(self.values.value)) != (nz := len(self.zones.value)):
                raise ValueError(f"Number od values in {self} ({nv}) does not match the number of zones ({nz})")

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'zones', Zone)
        obj.add_dependent_objects_from_config(config, 'axis', Axis, single=True)
        obj.add_dependent_objects_from_config(config, 'source', single=True)

        obj.check_values_and_zones()

        return obj

