from datetime import datetime
import logging

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


logger = logging.getLogger(__name__)


class Origin(EFLR):
    set_type = 'ORIGIN'
    logical_record_type = LogicalRecordType.OLR
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, object_name: str, set_name: str = None, **kwargs):

        super().__init__(object_name, set_name)

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

        if "creation_time" not in kwargs:
            logger.info("Creation time ('creation_time') not specified; setting it to the current date and time")
            kwargs["creation_time"] = datetime.now()

        self.set_attributes(**kwargs)
