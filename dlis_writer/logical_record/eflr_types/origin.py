from datetime import datetime
from configparser import ConfigParser
from typing_extensions import Self
import logging

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


logger = logging.getLogger(__name__)


class Origin(EFLR):
    set_type = 'ORIGIN'
    logical_record_type = LogicalRecordType.OLR
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)
    dtime_formats = ["%Y/%m/%d %H:%M:%S", "%Y.%m.%d %H:%M:%S"]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.file_id = self._create_attribute('file_id')
        self.file_set_name = self._create_attribute('file_set_name')
        self.file_set_number = self._create_attribute('file_set_number', converter=int)
        self.file_number = self._create_attribute('file_number', converter=int)
        self.file_type = self._create_attribute('file_type')
        self.product = self._create_attribute('product')
        self.version = self._create_attribute('version')
        self.programs = self._create_attribute('programs')
        self.creation_time = self._create_attribute('creation_time', converter=self.parse_dtime)
        self.order_number = self._create_attribute('order_number')
        self.descent_number = self._create_attribute('descent_number', converter=int)
        self.run_number = self._create_attribute('run_number', converter=int)
        self.well_id = self._create_attribute('well_id', converter=int)
        self.well_name = self._create_attribute('well_name')
        self.field_name = self._create_attribute('field_name')
        self.producer_code = self._create_attribute('producer_code', converter=int)
        self.producer_name = self._create_attribute('producer_name')
        self.company = self._create_attribute('company')
        self.name_space_name = self._create_attribute('name_space_name')
        self.name_space_version = self._create_attribute('name_space_version', converter=int)

    @classmethod
    def parse_dtime(cls, dtime_string):
        if isinstance(dtime_string, datetime):
            return dtime_string

        if not isinstance(dtime_string, str):
            raise TypeError(f"Expected a str, got {type(dtime_string)}")

        for dtime_format in cls.dtime_formats:
            try:
                dtime = datetime.strptime(dtime_string, dtime_format)
            except ValueError:
                pass
            else:
                break
        else:
            # loop finished without breaking - no date format fitted to the string
            raise ValueError(f"Provided date time value does not conform to any of the allowed formats: "
                             f"{', '.join(fmt for fmt in cls.dtime_formats)}")

        return dtime

    @classmethod
    def from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().from_config(config)
        if not config.has_section("Origin.attributes") or "creation_time" not in config["Origin.attributes"].keys():
            logger.info("Creation time ('creation_time') not specified in the config; "
                        "setting it to the current date and time")
            obj.creation_time.value = datetime.now()

        return obj
