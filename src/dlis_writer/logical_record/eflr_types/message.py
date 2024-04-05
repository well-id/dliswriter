from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.internal_enums import EFLRType
from dlis_writer.logical_record.core.attribute import IdentAttribute, DTimeAttribute, NumericAttribute, TextAttribute


class MessageItem(EFLRItem):
    """Model an object being part of Message EFLR."""

    parent: "MessageSet"

    def __init__(self, name: str, parent: "MessageSet", **kwargs: Any) -> None:
        """Initialise MessageItem.

        Args:
            name        :   Name of the MessageItem.
            parent      :   Parent MessageSet of this MessageItem.
            **kwargs    :   Values of to be set as characteristics of the MessageItem Attributes.
        """

        self._type = IdentAttribute('_type')
        self.time = DTimeAttribute('time', allow_float=True)
        self.borehole_drift = NumericAttribute('borehole_drift')
        self.vertical_depth = NumericAttribute('vertical_depth')
        self.radial_drift = NumericAttribute('radial_drift')
        self.angular_drift = NumericAttribute('angular_drift')
        self.text = TextAttribute('text', multivalued=True)

        super().__init__(name, parent=parent, **kwargs)


class MessageSet(EFLRSet):
    """Model Message EFLR."""

    set_type = 'MESSAGE'
    logical_record_type = EFLRType.SCRIPT
    item_type = MessageItem


class CommentItem(EFLRItem):
    """Model an object being part of Comment EFLR."""

    parent: "CommentSet"

    def __init__(self, name: str, parent: "CommentSet", **kwargs: Any) -> None:
        """Initialise CommentItem.

        Args:
            name        :   Name of the CommentItem.
            parent      :   Parent CommentSet of this CommentItem.
            **kwargs    :   Values of to be set as characteristics of the CommentItem Attributes.
        """

        self.text = TextAttribute('text', multivalued=True)

        super().__init__(name, parent=parent, **kwargs)


class CommentSet(EFLRSet):
    """Model Comment EFLR."""

    set_type = 'COMMENT'
    logical_record_type = EFLRType.SCRIPT
    item_type = CommentItem


MessageItem.parent_eflr_class = MessageSet
CommentItem.parent_eflr_class = CommentSet
