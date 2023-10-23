from datetime import datetime
import logging

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


logger = logging.getLogger(__name__)


class Origin(EFLR):
    set_type = 'ORIGIN'
    logical_record_type = LogicalRecordType.OLR

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.file_id = self._create_attribute('file_id', representation_code=RepC.ASCII)
        self.file_set_name = self._create_attribute('file_set_name', representation_code=RepC.IDENT)
        self.file_set_number = self._create_attribute('file_set_number', converter=int, representation_code=RepC.UVARI)
        self.file_number = self._create_attribute('file_number', converter=int, representation_code=RepC.UVARI)
        self.file_type = self._create_attribute('file_type', representation_code=RepC.IDENT)
        self.product = self._create_attribute('product', representation_code=RepC.ASCII)
        self.version = self._create_attribute('version', representation_code=RepC.ASCII)
        self.programs = self._create_attribute('programs', representation_code=RepC.ASCII)
        self.creation_time = self._create_attribute('creation_time', converter=self.parse_dtime, representation_code=RepC.DTIME)
        self.order_number = self._create_attribute('order_number', representation_code=RepC.ASCII)
        self.descent_number = self._create_attribute('descent_number', converter=int, representation_code=RepC.UNORM)
        self.run_number = self._create_attribute('run_number', converter=int, representation_code=RepC.UNORM)
        self.well_id = self._create_attribute('well_id', converter=int, representation_code=RepC.UNORM)
        self.well_name = self._create_attribute('well_name', representation_code=RepC.ASCII)
        self.field_name = self._create_attribute('field_name', representation_code=RepC.ASCII)
        self.producer_code = self._create_attribute('producer_code', converter=int, representation_code=RepC.UNORM)
        self.producer_name = self._create_attribute('producer_name', representation_code=RepC.ASCII)
        self.company = self._create_attribute('company', representation_code=RepC.ASCII)
        self.name_space_name = self._create_attribute('name_space_name', representation_code=RepC.IDENT)
        self.name_space_version = self._create_attribute('name_space_version', converter=int, representation_code=RepC.UVARI)

        if "creation_time" not in kwargs:
            logger.info("Creation time ('creation_time') not specified; setting it to the current date and time")
            kwargs["creation_time"] = datetime.now()

        self.set_attributes(**kwargs)
