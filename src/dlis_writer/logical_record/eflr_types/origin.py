from datetime import datetime
import logging
from typing import Any
import numpy as np

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.utils.struct_writer import ULONG_OFFSET
from dlis_writer.utils.types import number_type
from dlis_writer.logical_record.core.attribute import DTimeAttribute, NumericAttribute, TextAttribute, IdentAttribute


logger = logging.getLogger(__name__)


class OriginItem(EFLRItem):
    """Model an object being part of Origin EFLR."""

    parent: "OriginSet"

    def __init__(self, name: str, parent: "OriginSet", **kwargs: Any) -> None:
        """Initialise OriginItem.

        Args:
            name            :   Name of the OriginItem.
            parent          :   Parent OriginSet of this OriginItem.
            **kwargs        :   Values of to be set as characteristics of the OriginItem Attributes.
        """

        self.file_id = TextAttribute('file_id')
        self.file_set_name = IdentAttribute('file_set_name')
        self.file_set_number = NumericAttribute(
            'file_set_number', representation_code=RepC.UVARI, converter=self._no_reassign_file_set_number)
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

        super().__init__(name, parent=parent, **kwargs)

        if self.file_set_number.value is None:
            # repr code for file set number is UVARI, so USHORT/UNORM/ULONG; ULONG is the largest
            max_val = np.iinfo(np.uint32).max - ULONG_OFFSET
            v = np.random.randint(1, max_val)
            logger.info(f"File set number for {self} not specified; setting it to a randomly generated number: {v}")
            self.file_set_number.value = v

        if self._origin_reference is not None:
            if self._origin_reference != self.file_set_number.value:
                raise ValueError("Origin reference of an Origin should be the same as it's own file set number; "
                                 f"got {self._origin_reference} and {self.file_set_number.value}")
        else:
            self._origin_reference = self.file_set_number.value

        if self.creation_time.value is None:
            logger.info("Creation time ('creation_time') not specified; setting it to the current date and time")
            self.creation_time.value = datetime.now()

    def _set_defaults(self) -> None:
        if self.field_name.value is None:
            self.field_name.value = 'WILDCAT'  # according to RP66

    def _no_reassign_file_set_number(self, v: number_type) -> number_type:
        if self.file_set_number.value is not None:
            raise RuntimeError("File set number should not be reassigned; to have an alternative file set number, "
                               "please pass it to the OriginItem constructor")
        return v


class OriginSet(EFLRSet):
    """Model Origin EFLR."""

    set_type = 'ORIGIN'
    logical_record_type = EFLRType.OLR
    item_type = OriginItem


OriginItem.parent_eflr_class = OriginSet
