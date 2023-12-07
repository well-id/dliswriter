from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, DTimeAttribute, NumericAttribute


class MessageObject(EFLRObject):
    """Model an object being part of Message EFLR."""

    parent: "Message"

    def __init__(self, name: str, **kwargs):
        """Initialise MessageObject.

        Args:
            name        :   Name of the MessageObject.
            **kwargs    :   Values of to be set as characteristics of the MessageObject Attributes.
        """

        self._type = Attribute('_type', representation_code=RepC.IDENT, parent_eflr=self)
        self.time = DTimeAttribute('time', allow_float=True, parent_eflr=self)
        self.borehole_drift = NumericAttribute('borehole_drift', parent_eflr=self)
        self.vertical_depth = NumericAttribute('vertical_depth', parent_eflr=self)
        self.radial_drift = NumericAttribute('radial_drift', parent_eflr=self)
        self.angular_drift = NumericAttribute('angular_drift', parent_eflr=self)
        self.text = Attribute('text', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class Message(EFLR):
    """Model Message EFLR."""

    set_type = 'MESSAGE'
    logical_record_type = EFLRType.SCRIPT
    object_type = MessageObject


class CommentObject(EFLRObject):
    """Model an object being part of Comment EFLR."""

    parent: "Comment"

    def __init__(self, name: str, **kwargs):
        """Initialise CommentObject.

        Args:
            name        :   Name of the CommentObject.
            **kwargs    :   Values of to be set as characteristics of the CommentObject Attributes.
        """

        self.text = Attribute('text', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class Comment(EFLR):
    """Model Comment EFLR."""

    set_type = 'COMMENT'
    logical_record_type = EFLRType.SCRIPT
    object_type = CommentObject


MessageObject.parent_eflr_class = Message
CommentObject.parent_eflr_class = Comment
