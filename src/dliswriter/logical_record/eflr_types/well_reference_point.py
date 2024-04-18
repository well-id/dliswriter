"""From RP66 v1:

"""

from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.utils.internal.internal_enums import EFLRType, RepresentationCode as RepC
from dliswriter.logical_record.core.attribute import NumericAttribute, TextAttribute


class WellReferencePointItem(EFLRItem):
    """Model an object being part of WellReferencePoint EFLR."""

    parent: "WellReferencePointSet"

    def __init__(self, name: str, parent: "WellReferencePointSet", **kwargs: Any) -> None:
        """Initialise WellReferencePointItem.

        Args:
            name        :   Name of the WellReferencePointItem.
            parent      :   Parent WellReferencePointSet of this WellReferencePointItem.
            **kwargs    :   Values of to be set as characteristics of the WellReferencePointItem Attributes.
        """

        self.permanent_datum = TextAttribute('permanent_datum')
        self.vertical_zero = TextAttribute('vertical_zero')
        self.permanent_datum_elevation = NumericAttribute('permanent_datum_elevation', representation_code=RepC.FDOUBL)
        self.above_permanent_datum = NumericAttribute('above_permanent_datum', representation_code=RepC.FDOUBL)
        self.magnetic_declination = NumericAttribute('magnetic_declination', representation_code=RepC.FDOUBL)
        self.coordinate_1_name = TextAttribute('coordinate_1_name')
        self.coordinate_1_value = NumericAttribute('coordinate_1_value', representation_code=RepC.FDOUBL)
        self.coordinate_2_name = TextAttribute('coordinate_2_name')
        self.coordinate_2_value = NumericAttribute('coordinate_2_value', representation_code=RepC.FDOUBL)
        self.coordinate_3_name = TextAttribute('coordinate_3_name')
        self.coordinate_3_value = NumericAttribute('coordinate_3_value', representation_code=RepC.FDOUBL)

        super().__init__(name, parent=parent, **kwargs)


class WellReferencePointSet(EFLRSet):
    """Model WellReferencePoint EFLR."""

    set_type = 'WELL-REFERENCE'
    logical_record_type = EFLRType.OLR
    item_type = WellReferencePointItem


WellReferencePointItem.parent_eflr_class = WellReferencePointSet
