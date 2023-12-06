import logging
from typing import Union

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute, DimensionAttribute


logger = logging.getLogger(__name__)


class ParameterObject(EFLRObject):
    """Model an object being part of Parameter EFLR."""

    parent: "Parameter"
    
    def __init__(self, name: str, parent: "Parameter", **kwargs):
        """Initialise ParameterObject.

        Args:
            name        :   Name of the ParameterObject.
            parent      :   Parameter EFLR instance this ParameterObject belongs to.
            **kwargs    :   Values of to be set as characteristics of the ParameterObject Attributes.
        """

        self.long_name = Attribute('long_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.dimension = DimensionAttribute('dimension', parent_eflr=self)
        self.axis = EFLRAttribute('axis', object_class=Axis, multivalued=True, parent_eflr=self)
        self.zones = EFLRAttribute('zones', object_class=Zone, multivalued=True, parent_eflr=self)
        self.values = Attribute('values', converter=self.convert_maybe_numeric, multivalued=True, parent_eflr=self)

        super().__init__(name, parent, **kwargs)

        self._set_defaults()

    def _set_defaults(self):
        """Set default values of some attributes if no values have been set so far."""

        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]


class Parameter(EFLR):
    """Model Parameter EFLR."""

    set_type = 'PARAMETER'
    logical_record_type = EFLRType.STATIC
    object_type = ParameterObject

