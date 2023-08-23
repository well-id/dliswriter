from dlis_writer.logical_record.core import EFLR


class Zone(EFLR):
    set_type = 'ZONE'

    def __init__(self, *args, **kwargs):
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

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'STATIC'

        self.description = None
        self.domain = None
        self.maximum = None
        self.minimum = None

        self.create_attributes()
