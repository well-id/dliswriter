from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


class NoFormatObject(EFLRObject):
    """Model an object being part of NoFormat EFLR."""

    def __init__(self, name: str, parent: "NoFormat", **kwargs):
        """Initialise NoFormatObject.

        Args:
            name        :   Name of the NoFormatObject.
            parent      :   NoFormat EFLR instance this NoFormatObject belongs to.
            **kwargs    :   Values of to be set as characteristics of the NoFormatObject Attributes.
        """

        self.consumer_name = Attribute('consumer_name', representation_code=RepC.IDENT, parent_eflr=self)
        self.description = Attribute('description', representation_code=RepC.ASCII, parent_eflr=self)

        super().__init__(name, parent, **kwargs)


class NoFormat(EFLR):
    """Model NoFormat EFLR."""
    
    set_type = 'NO-FORMAT'
    logical_record_type = EFLRType.UDI
    object_type = NoFormatObject
