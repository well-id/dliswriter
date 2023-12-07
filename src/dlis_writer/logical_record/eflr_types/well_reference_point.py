from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute


class WellReferencePointObject(EFLRObject):
    """Model an object being part of WellReferencePoint EFLR."""

    parent: "WellReferencePoint"

    def __init__(self, name: str, **kwargs):
        """Initialise WellReferencePointObject.

        Args:
            name        :   Name of the WellReferencePointObject.
            **kwargs    :   Values of to be set as characteristics of the WellReferencePointObject Attributes.
        """

        self.permanent_datum = Attribute(
            'permanent_datum', representation_code=RepC.ASCII, parent_eflr=self)
        self.vertical_zero = Attribute(
            'vertical_zero', representation_code=RepC.ASCII, parent_eflr=self)
        self.permanent_datum_elevation = NumericAttribute(
            'permanent_datum_elevation', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.above_permanent_datum = NumericAttribute(
            'above_permanent_datum', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.magnetic_declination = NumericAttribute(
            'magnetic_declination', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.coordinate_1_name = Attribute(
            'coordinate_1_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.coordinate_1_value = NumericAttribute(
            'coordinate_1_value', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.coordinate_2_name = Attribute(
            'coordinate_2_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.coordinate_2_value = NumericAttribute(
            'coordinate_2_value', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.coordinate_3_name = Attribute(
            'coordinate_3_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.coordinate_3_value = NumericAttribute(
            'coordinate_3_value', representation_code=RepC.FDOUBL, parent_eflr=self)

        super().__init__(name, **kwargs)


class WellReferencePoint(EFLR):
    """Model WellReferencePoint EFLR."""

    set_type = 'WELL-REFERENCE'
    logical_record_type = EFLRType.OLR
    object_type = WellReferencePointObject


WellReferencePointObject.parent_eflr_class = WellReferencePoint
