from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode
from dlis_writer.logical_record.core.attribute import IdentAttribute, DTimeAttribute, TextAttribute


class ZoneItem(EFLRItem):
    """Model an object being part of Zone EFLR."""

    parent: "ZoneSet"

    domains = ('BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH')  #: allowed values for 'domain' Attribute

    def __init__(self, name: str, parent: "ZoneSet", **kwargs: Any) -> None:
        """Initialise ZoneItem.

        Args:
            name        :   Name of the ZoneItem.
            parent      :   Parent ZoneSet of this ZoneItem.
            **kwargs    :   Values of to be set as characteristics of the ZoneItem Attributes.
        """

        self.description = TextAttribute('description')
        self.domain = IdentAttribute('domain', converter=self.check_domain)
        self.maximum = DTimeAttribute('maximum', allow_float=True)
        self.minimum = DTimeAttribute('minimum', allow_float=True)

        super().__init__(name, parent=parent, **kwargs)

    @classmethod
    def check_domain(cls, domain: str) -> str:
        """Check that the provided 'domain' value is allowed by the standard. Raise a ValueError otherwise."""

        if domain not in cls.domains:
            raise ValueError(f"'domain' should be one of: {', '.join(cls.domains)}; got {domain}")
        return domain

    def _set_defaults(self) -> None:
        """Check maximum and minimum vs domain before writing the object."""

        domain = self.domain.value

        if domain is None:
            return

        rcs = [self.maximum.representation_code, self.minimum.representation_code]
        rcs = [rc for rc in rcs if rc is not None]
        if not rcs:
            return

        codes_are_dtime = [rc is RepresentationCode.DTIME for rc in rcs]

        if domain == 'TIME':
            if any(codes_are_dtime) and not all(codes_are_dtime):
                raise RuntimeError(f"{self}: either both or none of Zone's maximum and minimum should be of datetime "
                                   f"type; got {self.minimum.value} and {self.maximum.value}")

        else:
            if any(codes_are_dtime):
                raise RuntimeError(f"{self}: domain is '{domain}', so only float values for minimum and maximum "
                                   f"are allowed")


class ZoneSet(EFLRSet):
    """Model Zone EFLR."""

    set_type = 'ZONE'
    logical_record_type = EFLRType.STATIC
    item_type = ZoneItem


ZoneItem.parent_eflr_class = ZoneSet
