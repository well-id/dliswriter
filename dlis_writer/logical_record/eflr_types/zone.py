from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, DTimeAttribute


class ZoneObject(EFLRObject):
    set_type = 'ZONE'
    logical_record_type = EFLRType.STATIC
    domains = ('BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH')

    def __init__(self, name: str, parent: "Zone", **kwargs):
        """

        :description -> str

        :domain -> 3 options:
            BOREHOLE-DEPTH
            TIME
            VERTICAL-DEPTH

        :maximum -> Depending on the 'domain' attribute, this is either
        max-depth (dtype: float) or the latest time (dtype: datetime.datetime)

        :minimum -> Depending on the 'domain' attribute, this is either
        min-depth (dtype: float) or the earliest time (dtype: datetime.datetime)

        """

        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)
        self.domain = Attribute('domain', converter=self.check_domain, representation_code=RepC.IDENT, parent_eflr=self)
        self.maximum = DTimeAttribute('maximum', allow_float=True, parent_eflr=self)
        self.minimum = DTimeAttribute('minimum', allow_float=True, parent_eflr=self)

        super().__init__(name, parent, **kwargs)

    @classmethod
    def check_domain(cls, domain):
        if domain not in cls.domains:
            raise ValueError(f"'domain' should be one of: {', '.join(cls.domains)}; got {domain}")
        return domain


class Zone(EFLR):
    set_type = 'ZONE'
    logical_record_type = EFLRType.STATIC
    object_type = ZoneObject
