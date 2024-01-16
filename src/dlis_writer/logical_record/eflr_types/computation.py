import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRItem, EFLRSet
from dlis_writer.logical_record.eflr_types.axis import AxisSet
from dlis_writer.logical_record.eflr_types.zone import ZoneSet
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import (EFLRAttribute, NumericAttribute, DimensionAttribute, Attribute,
                                                       TextAttribute)


logger = logging.getLogger(__name__)


class ComputationItem(EFLRItem):
    """Model an object being part of Computation EFLR."""

    parent: "ComputationSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise ComputationItem.

        Args:
            name            :   Name of the ComputationItem.
            **kwargs        :   Values of to be set as characteristics of the ComputationItem Attributes.
        """

        self.long_name = TextAttribute('long_name', parent_eflr=self)
        self.properties = Attribute('properties', representation_code=RepC.IDENT, multivalued=True, parent_eflr=self)
        self.dimension = DimensionAttribute('dimension', parent_eflr=self)
        self.axis = EFLRAttribute('axis', object_class=AxisSet, parent_eflr=self)
        self.zones = EFLRAttribute('zones', object_class=ZoneSet, multivalued=True, parent_eflr=self)
        self.values = NumericAttribute('values', multivalued=True, parent_eflr=self)
        self.source = EFLRAttribute('source', parent_eflr=self)

        super().__init__(name, **kwargs)

        self._set_defaults()
        self.check_values_and_zones()

    def _set_defaults(self) -> None:
        """Set up default values of ComputationItem parameters if not explicitly set previously."""

        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]

    def check_values_and_zones(self) -> None:
        """Check that the currently set values and zones attributes match in sizes."""

        if self.values.value is not None and self.zones.value is not None:
            if (nv := len(self.values.value)) != (nz := len(self.zones.value)):
                raise ValueError(f"Number od values in {self} ({nv}) does not match the number of zones ({nz})")


class ComputationSet(EFLRSet):
    """Model Computation EFLR."""

    set_type = 'COMPUTATION'
    logical_record_type = EFLRType.STATIC
    item_type = ComputationItem


ComputationItem.parent_eflr_class = ComputationSet
