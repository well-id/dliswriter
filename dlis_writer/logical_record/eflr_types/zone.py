from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, DTimeAttribute


class Zone(EFLR):
    set_type = 'ZONE'
    logical_record_type = EFLRType.STATIC
    domains = ('BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH')

    def __init__(self, name: str, set_name: str = None, **kwargs):
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

        super().__init__(name, set_name)

        self.description = Attribute('description', representation_code=RepC.ASCII)
        self.domain = Attribute('domain', converter=self.check_domain, representation_code=RepC.IDENT)
        self.maximum = DTimeAttribute('maximum', allow_float=True)
        self.minimum = DTimeAttribute('minimum', allow_float=True)

        self.set_attributes(**kwargs)

    @classmethod
    def check_domain(cls, domain):
        if domain not in cls.domains:
            raise ValueError(f"'domain' should be one of: {', '.join(cls.domains)}; got {domain}")
        return domain

