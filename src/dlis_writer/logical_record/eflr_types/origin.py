from datetime import datetime
import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import DTimeAttribute, NumericAttribute, TextAttribute, IdentAttribute


logger = logging.getLogger(__name__)


class OriginItem(EFLRItem):
    """Model an object being part of Origin EFLR."""

    parent: "OriginSet"

    def __init__(self, name: str, file_set_number: int, **kwargs: Any) -> None:
        """Initialise OriginItem.

        Args:
            name            :   Name of the OriginItem.
            file_set_number :   ID by which other objects will refer to this origin.
            **kwargs        :   Values of to be set as characteristics of the OriginItem Attributes.
        """

        self.file_id = TextAttribute('file_id')
        self.file_set_name = IdentAttribute('file_set_name')
        self.file_set_number = NumericAttribute('file_set_number', representation_code=RepC.UVARI)
        self.file_number = NumericAttribute('file_number', representation_code=RepC.UVARI)
        self.file_type = IdentAttribute('file_type')
        self.product = TextAttribute('product')
        self.version = TextAttribute('version')
        self.programs = TextAttribute('programs', multivalued=True)
        self.creation_time = DTimeAttribute('creation_time')
        self.order_number = TextAttribute('order_number')
        self.descent_number = NumericAttribute('descent_number', representation_code=RepC.UNORM)
        self.run_number = NumericAttribute('run_number', representation_code=RepC.UNORM)
        self.well_id = NumericAttribute('well_id', representation_code=RepC.UNORM)
        self.well_name = TextAttribute('well_name')
        self.field_name = TextAttribute('field_name')
        self.producer_code = NumericAttribute('producer_code', representation_code=RepC.UNORM)
        self.producer_name = TextAttribute('producer_name')
        self.company = TextAttribute('company')
        self.name_space_name = IdentAttribute('name_space_name')
        self.name_space_version = NumericAttribute('name_space_version', representation_code=RepC.UVARI)

        if "creation_time" not in kwargs:
            logger.info("Creation time ('creation_time') not specified; setting it to the current date and time")
            kwargs["creation_time"] = datetime.now()

        super().__init__(name, file_set_number=file_set_number, **kwargs)


class OriginSet(EFLRSet):
    """Model Origin EFLR."""

    set_type = 'ORIGIN'
    logical_record_type = EFLRType.OLR
    item_type = OriginItem


OriginItem.parent_eflr_class = OriginSet
