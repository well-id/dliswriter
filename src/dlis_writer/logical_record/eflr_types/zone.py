from datetime import datetime

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, DTimeAttribute


class ZoneObject(EFLRObject):
    """Model an object being part of Zone EFLR."""

    parent: "Zone"

    domains = ('BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH')  #: allowed values for 'domain' Attribute

    def __init__(self, name: str, parent: "Zone", **kwargs):
        """Initialise ZoneObject.

        Args:
            name        :   Name of the ZoneObject.
            parent      :   Zone EFLR instance this ZoneObject belongs to.
            **kwargs    :   Values of to be set as characteristics of the ZoneObject Attributes.
        """

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.domain = Attribute('domain', converter=self.check_domain, representation_code=RepC.IDENT, parent_eflr=self)
        self.maximum = DTimeAttribute('maximum', allow_float=True, parent_eflr=self)
        self.minimum = DTimeAttribute('minimum', allow_float=True, parent_eflr=self)

        super().__init__(name, parent, **kwargs)

        if self.domain.value == 'TIME':
            if not all(isinstance(v, (datetime, type(None))) for v in (self.minimum.value, self.minimum.value)):
                raise TypeError("Zone maximum and minimum should be instances of datetime.datetime")
        else:
            if not all(isinstance(v, ((int, float), type(None))) for v in (self.minimum.value, self.minimum.value)):
                raise TypeError("Zone maximum and minimum should be numbers")

    @classmethod
    def check_domain(cls, domain: str) -> str:
        """Check that the provided 'domain' value is allowed by the standard. Raise a ValueError otherwise."""

        if domain not in cls.domains:
            raise ValueError(f"'domain' should be one of: {', '.join(cls.domains)}; got {domain}")
        return domain


class Zone(EFLR):
    """Model Zone EFLR."""

    set_type = 'ZONE'
    logical_record_type = EFLRType.STATIC
    object_type = ZoneObject
