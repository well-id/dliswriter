from numbers import Number
from datetime import datetime, timedelta

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Zone(EFLR):
    set_type = 'ZONE'
    logical_record_type = LogicalRecordType.STATIC
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)
    _instance_dict = {}

    def __init__(self, object_name: str, set_name: str = None, **kwargs):
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

        super().__init__(object_name, set_name)

        self.description = self._create_attribute('description')
        self.domain = self._create_attribute('domain')
        self.maximum = self._create_attribute('maximum', converter=self.parse_number_or_dtime)
        self.minimum = self._create_attribute('minimum', converter=self.parse_number_or_dtime)

        self.set_attributes(**kwargs)

        self._instance_dict[object_name] = self

    @classmethod
    def parse_number_or_dtime(cls, value):
        if value is None:
            return value

        if isinstance(value, (Number, datetime, timedelta)):
            return value

        if not isinstance(value, str):
            raise TypeError(f"Expected a number, datetime, timedelta, or a string; got {type(value)}: {value}")

        for parser in (cls.parse_dtime, int, float):
            try:
                return parser(value)
            except ValueError:
                pass

        raise ValueError(f"Couldn't parse value: '{value}'")

    @classmethod
    def get_instance(cls, name):
        return cls._instance_dict.get(name)

    @classmethod
    def get_or_make_from_config(cls, name, config):
        if name in cls._instance_dict:
            return cls.get_instance(name)
        return cls.from_config(config, key=name)
