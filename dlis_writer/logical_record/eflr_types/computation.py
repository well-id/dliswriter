import logging

from dlis_writer.logical_record.core.eflr import EFLRObject, EFLR
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import *


logger = logging.getLogger(__name__)


class ComputationObject(EFLRObject):
    set_type = 'COMPUTATION'
    logical_record_type = EFLRType.STATIC

    def __init__(self, name: str, parent: "Computation", **kwargs):
        self.long_name = Attribute('long_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.properties = Attribute('properties', representation_code=RepC.IDENT, multivalued=True, parent_eflr=self)
        self.dimension = DimensionAttribute('dimension', parent_eflr=self)
        self.axis = EFLRAttribute('axis', object_class=Axis, parent_eflr=self)
        self.zones = EFLRAttribute('zones', object_class=Zone, multivalued=True, parent_eflr=self)
        self.values = NumericAttribute('values', multivalued=True, parent_eflr=self)
        self.source = EFLRAttribute('source', parent_eflr=self)

        super().__init__(name, parent, **kwargs)

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


class Computation(EFLR):
    set_type = 'COMPUTATION'
    logical_record_type = EFLRType.STATIC
    object_type = ComputationObject
