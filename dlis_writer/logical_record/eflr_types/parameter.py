from configparser import ConfigParser
from typing_extensions import Self
import logging

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute, DimensionAttribute


logger = logging.getLogger(__name__)


class ParameterObject(EFLRObject):
    set_type = 'PARAMETER'
    logical_record_type = EFLRType.STATIC

    def __init__(self, name: str, parent: "Parameter", **kwargs):

        self.long_name = Attribute('long_name', representation_code=RepC.ASCII)
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=Axis, multivalued=True)
        self.zones = EFLRAttribute('zones', object_class=Zone, multivalued=True)
        self.values = Attribute('values', converter=self.convert_value, multivalued=True)

        super().__init__(name, parent, **kwargs)

        self._set_defaults()

    def _set_defaults(self):
        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]

    @classmethod
    def convert_value(cls, val):
        try:
            val = Attribute.convert_numeric(val)
        except ValueError:
            pass
        return val


class Parameter(EFLR):
    set_type = 'PARAMETER'
    logical_record_type = EFLRType.STATIC
    object_type = ParameterObject

