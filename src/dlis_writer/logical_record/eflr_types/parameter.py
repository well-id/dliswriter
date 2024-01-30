import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.eflr_types.zone import ZoneSet
from dlis_writer.logical_record.eflr_types.axis import AxisSet
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute, DimensionAttribute, TextAttribute


logger = logging.getLogger(__name__)


class ParameterItem(EFLRItem):
    """Model an object being part of Parameter EFLR."""

    parent: "ParameterSet"

    def __init__(self, name: str, parent: "ParameterSet", **kwargs: Any) -> None:
        """Initialise ParameterItem.

        Args:
            name        :   Name of the ParameterItem.
            parent      :   Parent ParameterSet of this ParameterItem.
            **kwargs    :   Values of to be set as characteristics of the ParameterItem Attributes.
        """

        self.long_name = TextAttribute('long_name')
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=AxisSet, multivalued=True)
        self.zones = EFLRAttribute('zones', object_class=ZoneSet, multivalued=True)
        self.values = Attribute('values', converter=self.convert_maybe_numeric, multivalued=True)

        super().__init__(name, parent=parent, **kwargs)

    def _run_checks_and_set_defaults(self) -> None:
        """Set default values of some attributes if no values have been set so far."""

        if self.values.value is not None:
            if self.zones.value is not None:
                if (nv := self.values.count) != (nz := self.zones.count):
                    raise RuntimeError("A Parameter must have the same number of values and zones if both are "
                                       f"defined; got {nv} channels and {nz} zones in {self}")
            else:
                if (nv := self.values.count) > 1:
                    raise ValueError(f"{self} does not have any zones defined, so only a single value is permitted; "
                                     f"got {nv}: {self.values.value}")

        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]


class ParameterSet(EFLRSet):
    """Model Parameter EFLR."""

    set_type = 'PARAMETER'
    logical_record_type = EFLRType.STATIC
    item_type = ParameterItem


ParameterItem.parent_eflr_class = ParameterSet
