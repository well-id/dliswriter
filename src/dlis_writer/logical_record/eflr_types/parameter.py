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

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise ParameterItem.

        Args:
            name        :   Name of the ParameterItem.
            **kwargs    :   Values of to be set as characteristics of the ParameterItem Attributes.
        """

        self.long_name = TextAttribute('long_name', parent_eflr=self)
        self.dimension = DimensionAttribute('dimension', parent_eflr=self)
        self.axis = EFLRAttribute('axis', object_class=AxisSet, multivalued=True, parent_eflr=self)
        self.zones = EFLRAttribute('zones', object_class=ZoneSet, multivalued=True, parent_eflr=self)
        self.values = Attribute('values', converter=self.convert_maybe_numeric, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)

        self._set_defaults()

    def _set_defaults(self) -> None:
        """Set default values of some attributes if no values have been set so far."""

        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]


class ParameterSet(EFLRSet):
    """Model Parameter EFLR."""

    set_type = 'PARAMETER'
    logical_record_type = EFLRType.STATIC
    item_type = ParameterItem


ParameterItem.parent_eflr_class = ParameterSet
