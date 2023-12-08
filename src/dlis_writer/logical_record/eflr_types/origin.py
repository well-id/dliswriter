from datetime import datetime
import logging

from dlis_writer.logical_record.core.eflr import EFLRTable, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, DTimeAttribute, NumericAttribute


logger = logging.getLogger(__name__)


class OriginItem(EFLRItem):
    """Model an object being part of Origin EFLR."""

    parent: "OriginTable"

    def __init__(self, name: str, **kwargs):
        """Initialise OriginObject.

        Args:
            name        :   Name of the OriginObject.
            **kwargs    :   Values of to be set as characteristics of the OriginObject Attributes.
        """

        self.file_id = Attribute('file_id', representation_code=RepC.ASCII, parent_eflr=self)
        self.file_set_name = Attribute('file_set_name', representation_code=RepC.IDENT, parent_eflr=self)
        self.file_set_number = NumericAttribute('file_set_number', representation_code=RepC.UVARI, parent_eflr=self)
        self.file_number = NumericAttribute('file_number', representation_code=RepC.UVARI, parent_eflr=self)
        self.file_type = Attribute('file_type', representation_code=RepC.IDENT, parent_eflr=self)
        self.product = Attribute('product', representation_code=RepC.ASCII, parent_eflr=self)
        self.version = Attribute('version', representation_code=RepC.ASCII, parent_eflr=self)
        self.programs = Attribute('programs', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)
        self.creation_time = DTimeAttribute('creation_time', parent_eflr=self)
        self.order_number = Attribute('order_number', representation_code=RepC.ASCII, parent_eflr=self)
        self.descent_number = NumericAttribute('descent_number', representation_code=RepC.UNORM, parent_eflr=self)
        self.run_number = NumericAttribute('run_number', representation_code=RepC.UNORM, parent_eflr=self)
        self.well_id = NumericAttribute('well_id', representation_code=RepC.UNORM, parent_eflr=self)
        self.well_name = Attribute('well_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.field_name = Attribute('field_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.producer_code = NumericAttribute('producer_code', representation_code=RepC.UNORM, parent_eflr=self)
        self.producer_name = Attribute('producer_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.company = Attribute('company', representation_code=RepC.ASCII, parent_eflr=self)
        self.name_space_name = Attribute('name_space_name', representation_code=RepC.IDENT, parent_eflr=self)
        self.name_space_version = NumericAttribute(
            'name_space_version', representation_code=RepC.UVARI, parent_eflr=self)

        if "creation_time" not in kwargs:
            logger.info("Creation time ('creation_time') not specified; setting it to the current date and time")
            kwargs["creation_time"] = datetime.now()

        super().__init__(name, **kwargs)


class OriginTable(EFLRTable):
    """Model Origin EFLR."""

    set_type = 'ORIGIN'
    logical_record_type = EFLRType.OLR
    object_type = OriginItem


OriginItem.parent_eflr_class = OriginTable
