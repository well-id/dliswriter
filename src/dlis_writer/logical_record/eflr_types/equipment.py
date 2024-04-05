from typing import Any
import logging

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.internal_enums import EFLRType
from dlis_writer.utils.enums import EquipmentType, EquipmentLocation
from dlis_writer.logical_record.core.attribute import NumericAttribute, StatusAttribute, TextAttribute, IdentAttribute
from dlis_writer.utils.value_checkers import validate_string


logger = logging.getLogger(__name__)


class EquipmentItem(EFLRItem):
    """Model an object being part of Equipment EFLR."""

    parent: "EquipmentSet"

    def __init__(self, name: str, parent: "EquipmentSet", **kwargs: Any) -> None:
        """Initialise EquipmentItem.

        Args:
            name        :   Name of the EquipmentItem.
            parent      :   Parent EquipmentSet of this EquipmentItem.
            **kwargs    :   Values of to be set as characteristics of the EquipmentItem Attributes.
        """

        self.trademark_name = TextAttribute('trademark_name')
        self.status = StatusAttribute('status')
        self._type = IdentAttribute(
            '_type', converter=EquipmentType.make_converter("equipment types", soft=True))
        self.serial_number = IdentAttribute('serial_number', converter=validate_string)
        self.location = IdentAttribute(
            'location', converter=EquipmentLocation.make_converter("equipment locations", soft=True))
        self.height = NumericAttribute('height')
        self.length = NumericAttribute('length')
        self.minimum_diameter = NumericAttribute('minimum_diameter')
        self.maximum_diameter = NumericAttribute('maximum_diameter')
        self.volume = NumericAttribute('volume')
        self.weight = NumericAttribute('weight')
        self.hole_size = NumericAttribute('hole_size')
        self.pressure = NumericAttribute('pressure')
        self.temperature = NumericAttribute('temperature')
        self.vertical_depth = NumericAttribute('vertical_depth')
        self.radial_drift = NumericAttribute('radial_drift')
        self.angular_drift = NumericAttribute('angular_drift')

        super().__init__(name, parent=parent, **kwargs)


class EquipmentSet(EFLRSet):
    """Model Equipment EFLR."""

    set_type = 'EQUIPMENT'
    logical_record_type = EFLRType.STATIC
    item_type = EquipmentItem


EquipmentItem.parent_eflr_class = EquipmentSet
