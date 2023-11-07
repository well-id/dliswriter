import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import *


logger = logging.getLogger(__name__)


class Computation(EFLR):
    set_type = 'COMPUTATION'
    logical_record_type = EFLRType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.long_name = Attribute('long_name', representation_code=RepC.ASCII)
        self.properties = Attribute('properties', representation_code=RepC.IDENT, multivalued=True)
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=Axis)
        self.zones = EFLRAttribute('zones', object_class=Zone, multivalued=True)
        self.values = NumericAttribute('values', multivalued=True)
        self.source = EFLRAttribute('source')

        self.set_attributes(**kwargs)
        self._set_defaults()
        self.check_values_and_zones()

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

        for attr in (obj.axis, obj.zones, obj.source):
            attr.finalise_from_config(config)

        return obj

