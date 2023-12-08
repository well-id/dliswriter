import logging

from dlis_writer.logical_record.core.eflr import EFLRTable, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.zone import ZoneTable
from dlis_writer.logical_record.eflr_types.axis import AxisTable
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute, DimensionAttribute


logger = logging.getLogger(__name__)


class ParameterItem(EFLRItem):
    """Model an object being part of Parameter EFLR."""

    parent: "ParameterTable"
    
    def __init__(self, name: str, **kwargs):
        """Initialise ParameterObject.

        Args:
            name        :   Name of the ParameterObject.
            **kwargs    :   Values of to be set as characteristics of the ParameterObject Attributes.
        """

        self.long_name = Attribute('long_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.dimension = DimensionAttribute('dimension', parent_eflr=self)
        self.axis = EFLRAttribute('axis', object_class=AxisTable, multivalued=True, parent_eflr=self)
        self.zones = EFLRAttribute('zones', object_class=ZoneTable, multivalued=True, parent_eflr=self)
        self.values = Attribute('values', converter=self.convert_maybe_numeric, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)

        self._set_defaults()

    def _set_defaults(self):
        """Set default values of some attributes if no values have been set so far."""

        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]


class ParameterTable(EFLRTable):
    """Model Parameter EFLR."""

    set_type = 'PARAMETER'
    logical_record_type = EFLRType.STATIC
    item_type = ParameterItem


ParameterItem.parent_eflr_class = ParameterTable
