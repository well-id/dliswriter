from typing import Any
import logging

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import NumericAttribute, StatusAttribute, TextAttribute, IdentAttribute


logger = logging.getLogger(__name__)


class EquipmentItem(EFLRItem):
    """Model an object being part of Equipment EFLR."""

    parent: "EquipmentSet"

    #: options for the 'type' ('_type') attribute, allowed by the standard
    TYPE_OPTIONS = (
        "Adapter",
        "Board",
        "Bottom-Nose",
        "Bridle",
        "Cable",
        "Calibrator",
        "Cartridge",
        "Centralizer",
        "Chamber",
        "Cushion",
        "Depth-Device",
        "Display",
        "Drawer",
        "Excentralizer",
        "Explosive-Source",
        "Flask",
        "Geophone",
        "Gun",
        "Head",
        "Housing",
        "Jig",
        "Joint",
        "Nuclear-Detector",
        "Packer",
        "Pad",
        "Panel",
        "Positioning",
        "Printer",
        "Radioactive-Source",
        "Shield",
        "Simulator",
        "Skid",
        "Sonde",
        "Spacer",
        "Standoff",
        "System",
        "Tool",
        "Tool-Module",
        "Transducer",
        "Vibration-Source",
    )

    #: options for the 'location' attribute, allowed by the standard
    LOCATION_OPTIONS = (
        'Logging-System',
        'Remote',
        'Rig',
        'Well'
    )

    def __init__(self, name: str, parent: "EquipmentSet", **kwargs: Any) -> None:
        """Initialise EquipmentItem.

        Args:
            name        :   Name of the EquipmentItem.
            parent      :   Parent EquipmentSet of this EquipmentItem.
            **kwargs    :   Values of to be set as characteristics of the EquipmentItem Attributes.
        """

        self.trademark_name = TextAttribute('trademark_name')
        self.status = StatusAttribute('status')
        self._type = IdentAttribute('_type', converter=self._check_type)
        self.serial_number = IdentAttribute('serial_number')
        self.location = IdentAttribute('location', converter=self._check_location)
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

    @classmethod
    def _check_type(cls, v: str) -> str:
        if v not in cls.TYPE_OPTIONS:
            logger.warning(f"Equipment type should be one of the following: {', '.join(cls.TYPE_OPTIONS)}; got {v}")
        return v

    @classmethod
    def _check_location(cls, v: str) -> str:
        if v not in cls.LOCATION_OPTIONS:
            logger.warning(f"Equipment location should be one of the following: "
                           f"{', '.join(cls.LOCATION_OPTIONS)}; got {v}")
        return v


class EquipmentSet(EFLRSet):
    """Model Equipment EFLR."""

    set_type = 'EQUIPMENT'
    logical_record_type = EFLRType.STATIC
    item_type = EquipmentItem


EquipmentItem.parent_eflr_class = EquipmentSet
