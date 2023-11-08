from datetime import datetime
import logging

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, DTimeAttribute, NumericAttribute


logger = logging.getLogger(__name__)


class OriginObject(EFLRObject):
    def __init__(self, name: str, parent, **kwargs):

        self.file_id = Attribute('file_id', representation_code=RepC.ASCII)
        self.file_set_name = Attribute('file_set_name', representation_code=RepC.IDENT)
        self.file_set_number = NumericAttribute('file_set_number', representation_code=RepC.UVARI)
        self.file_number = NumericAttribute('file_number', representation_code=RepC.UVARI)
        self.file_type = Attribute('file_type', representation_code=RepC.IDENT)
        self.product = Attribute('product', representation_code=RepC.ASCII)
        self.version = Attribute('version', representation_code=RepC.ASCII)
        self.programs = Attribute('programs', representation_code=RepC.ASCII, multivalued=True)
        self.creation_time = DTimeAttribute('creation_time')
        self.order_number = Attribute('order_number', representation_code=RepC.ASCII)
        self.descent_number = NumericAttribute('descent_number', representation_code=RepC.UNORM)
        self.run_number = NumericAttribute('run_number', representation_code=RepC.UNORM)
        self.well_id = NumericAttribute('well_id', representation_code=RepC.UNORM)
        self.well_name = Attribute('well_name', representation_code=RepC.ASCII)
        self.field_name = Attribute('field_name', representation_code=RepC.ASCII)
        self.producer_code = NumericAttribute('producer_code', representation_code=RepC.UNORM)
        self.producer_name = Attribute('producer_name', representation_code=RepC.ASCII)
        self.company = Attribute('company', representation_code=RepC.ASCII)
        self.name_space_name = Attribute('name_space_name', representation_code=RepC.IDENT)
        self.name_space_version = NumericAttribute('name_space_version', representation_code=RepC.UVARI)

        if "creation_time" not in kwargs:
            logger.info("Creation time ('creation_time') not specified; setting it to the current date and time")
            kwargs["creation_time"] = datetime.now()

        super().__init__(name, parent, **kwargs)


class Origin(EFLR):
    set_type = 'ORIGIN'
    logical_record_type = EFLRType.OLR
    object_type = OriginObject
