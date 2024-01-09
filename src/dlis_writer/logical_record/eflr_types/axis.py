from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute


class AxisItem(EFLRItem):
    """Model an object being part of Axis EFLR."""

    parent: "AxisSet"

    def __init__(self, name: str, **kwargs):
        """Initialise AxisItem.

        Args:
            name        :   Name of the AxisItem.
            **kwargs    :   Values of to be set as characteristics of the AxisItem Attributes.
        """

        self.axis_id = Attribute('axis_id', representation_code=RepC.IDENT, parent_eflr=self)
        self.coordinates = Attribute('coordinates', multivalued=True, parent_eflr=self,
                                     converter=self.convert_maybe_numeric)
        self.spacing = NumericAttribute('spacing', parent_eflr=self)

        super().__init__(name, **kwargs)


class AxisSet(EFLRSet):
    """Model Axis EFLR."""

    set_type = 'AXIS'
    logical_record_type = EFLRType.AXIS
    item_type = AxisItem


AxisItem.parent_eflr_class = AxisSet
