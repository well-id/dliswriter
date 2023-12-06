from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute


class EquipmentObject(EFLRObject):
    """Model an object being part of Equipment EFLR."""

    parent: "Equipment"

    def __init__(self, name: str, parent: "Equipment", **kwargs):
        """Initialise EquipmentObject.

        Args:
            name        :   Name of the EquipmentObject.
            parent      :   Equipment EFLR instance this EquipmentObject belongs to.
            **kwargs    :   Values of to be set as characteristics of the EquipmentObject Attributes.
        """

        self.trademark_name = Attribute('trademark_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.status = Attribute('status', converter=int, representation_code=RepC.STATUS, parent_eflr=self)
        self._type = Attribute('_type', representation_code=RepC.IDENT, parent_eflr=self)
        self.serial_number = Attribute('serial_number', representation_code=RepC.IDENT, parent_eflr=self)
        self.location = Attribute('location', representation_code=RepC.IDENT, parent_eflr=self)
        self.height = NumericAttribute('height', parent_eflr=self)
        self.length = NumericAttribute('length', parent_eflr=self)
        self.minimum_diameter = NumericAttribute('minimum_diameter', parent_eflr=self)
        self.maximum_diameter = NumericAttribute('maximum_diameter', parent_eflr=self)
        self.volume = NumericAttribute('volume', parent_eflr=self)
        self.weight = NumericAttribute('weight', parent_eflr=self)
        self.hole_size = NumericAttribute('hole_size', parent_eflr=self)
        self.pressure = NumericAttribute('pressure', parent_eflr=self)
        self.temperature = NumericAttribute('temperature', parent_eflr=self)
        self.vertical_depth = NumericAttribute('vertical_depth', parent_eflr=self)
        self.radial_drift = NumericAttribute('radial_drift', parent_eflr=self)
        self.angular_drift = NumericAttribute('angular_drift', parent_eflr=self)

        super().__init__(name, parent, **kwargs)


class Equipment(EFLR):
    """Model Equipment EFLR."""

    set_type = 'EQUIPMENT'
    logical_record_type = EFLRType.STATIC
    object_type = EquipmentObject

