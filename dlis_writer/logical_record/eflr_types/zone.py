from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Zone(EFLR):
    set_type = 'ZONE'
    logical_record_type = LogicalRecordType.STATIC
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
        """

        :description -> str

        :domain -> 3 options:
            BOREHOLE-DEPTH
            TIME
            VERTICAL-DEPTH

        :maximum -> Depending on the 'domain' attribute, this is either
        max-depth (dtype: float) or the latest time (dtype: datetime.datetime)

        :minimum -> Dependng on the 'domain' attribute, this is either
        min-depth (dtype: float) or the earlieast time (dtype: datetime.datetime)

        """

        super().__init__(object_name, set_name)

        self.description = self._create_attribute('description')
        self.domain = self._create_attribute('domain')
        self.maximum = self._create_attribute('maximum')
        self.minimum = self._create_attribute('minimum')

        self.set_attributes(**kwargs)
