from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.internal_enums import EFLRType
from dlis_writer.logical_record.core.attribute import TextAttribute


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


CommentItem.parent_eflr_class = CommentSet
