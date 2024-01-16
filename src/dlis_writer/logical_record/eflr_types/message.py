from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import IdentAttribute, DTimeAttribute, NumericAttribute, TextAttribute


class MessageItem(EFLRItem):
    """Model an object being part of Message EFLR."""

    parent: "MessageSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise MessageItem.

        Args:
            name        :   Name of the MessageItem.
            **kwargs    :   Values of to be set as characteristics of the MessageItem Attributes.
        """

        self._type = IdentAttribute('_type', parent_eflr=self)
        self.time = DTimeAttribute('time', allow_float=True, parent_eflr=self)
        self.borehole_drift = NumericAttribute('borehole_drift', parent_eflr=self)
        self.vertical_depth = NumericAttribute('vertical_depth', parent_eflr=self)
        self.radial_drift = NumericAttribute('radial_drift', parent_eflr=self)
        self.angular_drift = NumericAttribute('angular_drift', parent_eflr=self)
        self.text = TextAttribute('text', multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class MessageSet(EFLRSet):
    """Model Message EFLR."""

    set_type = 'MESSAGE'
    logical_record_type = EFLRType.SCRIPT
    item_type = MessageItem


class CommentItem(EFLRItem):
    """Model an object being part of Comment EFLR."""

    parent: "CommentSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise CommentItem.

        Args:
            name        :   Name of the CommentItem.
            **kwargs    :   Values of to be set as characteristics of the CommentItem Attributes.
        """

        self.text = TextAttribute('text', multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class CommentSet(EFLRSet):
    """Model Comment EFLR."""

    set_type = 'COMMENT'
    logical_record_type = EFLRType.SCRIPT
    item_type = CommentItem


MessageItem.parent_eflr_class = MessageSet
CommentItem.parent_eflr_class = CommentSet
