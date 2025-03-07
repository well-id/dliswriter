from datetime import datetime
import logging
from typing import Any
import numpy as np

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.utils.internal.internal_enums import EFLRType, RepresentationCode as RepC
from dliswriter.utils.internal.struct_writer import ULONG_OFFSET
from dliswriter.utils.internal.types import number_type
from dliswriter.logical_record.core.attribute import DTimeAttribute, NumericAttribute, TextAttribute, IdentAttribute
from dliswriter.configuration import global_config


logger = logging.getLogger(__name__)


class OriginItem(EFLRItem):
    """Model an object being part of Origin EFLR."""

    parent: "OriginSet"

    def __init__(
        self,
        name: str,
        parent: "OriginSet",
        origin_reference: int,
        **kwargs: Any,
    ) -> None:
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

        super().__init__(
            name,
            parent=parent,
            origin_reference=origin_reference,
            **kwargs,
        )

        if self.file_set_number.value is None:
            logger.info(f"File set number for {self} not specified")
            if global_config.high_compat_mode:
                # there are poorly-understood issues related to the file set number when the file is opened in
                # Schlumberger's Log Data Composer; no such issues noticed when the file set number is 1
                # (or other low number)
                # the default file_set_number is the number of origins defined so far (for the current OriginSet)
                # (this includes the current OriginItem, so the lowest number is 1)
                n = self.parent.n_items
                logger.info(f"Setting file set number of {self} to {n}")
                self.file_set_number.value = n
            else:
                # according to the standard, file_set_number is a random integer taken from a large range
                # repr code for file_set_number is UVARI, so USHORT/UNORM/ULONG; ULONG is the largest
                max_val = np.iinfo(np.uint32).max - ULONG_OFFSET
                v = np.random.randint(1, max_val)
                logger.info(f"Setting file set number of {self} to a randomly generated number: {v}")
                self.file_set_number.value = v

        if self.creation_time.value is None:
            logger.info("Creation time ('creation_time') not specified; setting it to the current date and time")
            self.creation_time.value = datetime.now()

    def _run_checks_and_set_defaults(self) -> None:
        """Set a default field name value - if no field name has been defined."""

        if self.field_name.value is None:
            logger.debug(f"Setting field_name of {self} to the default value: 'WILDCAT'")
            self.field_name.value = 'WILDCAT'  # according to RP66

    def _no_reassign_file_set_number(self, v: number_type) -> number_type:
        """Value checker for file_set_number. Make sure the value is not reassigned."""

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
