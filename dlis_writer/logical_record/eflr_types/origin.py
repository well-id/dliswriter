from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Origin(EFLR):
    set_type = 'ORIGIN'
    logical_record_type = LogicalRecordType.OLR
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.file_id = self._create_attribute('file_id')
        self.file_set_name = self._create_attribute('file_set_name')
        self.file_set_number = self._create_attribute('file_set_number')
        self.file_number = self._create_attribute('file_number')
        self.file_type = self._create_attribute('file_type')
        self.product = self._create_attribute('product')
        self.version = self._create_attribute('version')
        self.programs = self._create_attribute('programs')
        self.creation_time = self._create_attribute('creation_time')
        self.order_number = self._create_attribute('order_number')
        self.descent_number = self._create_attribute('descent_number')
        self.run_number = self._create_attribute('run_number')
        self.well_id = self._create_attribute('well_id')
        self.well_name = self._create_attribute('well_name')
        self.field_name = self._create_attribute('field_name')
        self.producer_code = self._create_attribute('producer_code')
        self.producer_name = self._create_attribute('producer_name')
        self.company = self._create_attribute('company')
        self.name_space_name = self._create_attribute('name_space_name')
        self.name_space_version = self._create_attribute('name_space_version')
