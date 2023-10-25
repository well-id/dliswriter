from configparser import ConfigParser
from typing_extensions import Self
import logging

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.zone import Zone
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.logical_record.core.attribute import Attribute, EFLRAttribute, DimensionAttribute


logger = logging.getLogger(__name__)


class Parameter(EFLR):
    set_type = 'PARAMETER'
    logical_record_type = LogicalRecordType.STATIC

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.long_name = Attribute('long_name', representation_code=RepC.ASCII)
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=Axis, multivalued=True)
        self.zones = EFLRAttribute('zones', object_class=Zone, multivalued=True)
        self.values = Attribute('values', converter=self.convert_value, multivalued=True)

        self.set_attributes(**kwargs)
        self._set_defaults()

    def _set_defaults(self):
        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        for attr in (obj.axis, obj.zones):
            attr.finalise_from_config(config)

        return obj

    @classmethod
    def convert_value(cls, val):
        try:
            val = Attribute.convert_numeric(val)
        except ValueError:
            pass
        return val


