import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRItem, EFLRSet, DimensionedItem
from dlis_writer.logical_record.eflr_types.axis import AxisSet
from dlis_writer.logical_record.eflr_types.zone import ZoneSet
from dlis_writer.logical_record.eflr_types.long_name import LongNameSet
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import (EFLRAttribute, NumericAttribute, DimensionAttribute,
                                                       EFLROrTextAttribute, PropertiesAttribute)


logger = logging.getLogger(__name__)


class ComputationItem(EFLRItem, DimensionedItem):
    """Model an object being part of Computation EFLR."""

    parent: "ComputationSet"

    def __init__(self, name: str, parent: "ComputationSet", **kwargs: Any) -> None:
        """Initialise ComputationItem.

        Args:
            name            :   Name of the ComputationItem.
            parent          :   Parent ComputationSet of this ComputationItem.
            **kwargs        :   Values of to be set as characteristics of the ComputationItem Attributes.
        """

        self.long_name = EFLROrTextAttribute('long_name', object_class=LongNameSet)
        self.properties = PropertiesAttribute('properties')
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=AxisSet, multivalued=True)
        self.zones = EFLRAttribute('zones', object_class=ZoneSet, multivalued=True)
        self.values = NumericAttribute('values', multivalued=True, multidimensional=True)
        self.source = EFLRAttribute('source')

        super().__init__(name, parent=parent, **kwargs)

    def _run_checks_and_set_defaults(self) -> None:
        """Set up default values of ComputationItem parameters if not explicitly set previously."""

        if self.values.value is not None and self.zones.value is not None:
            if (nv := len(self.values.value)) != (nz := self.zones.count):
                raise RuntimeError("A Computation must have the same number of values and zones if both are "
                                   f"defined; got {nv} values and {nz} zones in {self}")

        self._check_axis_vs_dimension()
        self._check_or_set_value_dimensionality(self.values.value)

        if self.values.value and not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to [1]")
            self.dimension.value = [1]


class ComputationSet(EFLRSet):
    """Model Computation EFLR."""

    set_type = 'COMPUTATION'
    logical_record_type = EFLRType.STATIC
    item_type = ComputationItem


ComputationItem.parent_eflr_class = ComputationSet
