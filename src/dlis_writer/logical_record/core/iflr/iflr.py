from dlis_writer.utils.internal_enums import IFLRType
from dlis_writer.logical_record.core.logical_record import LogicalRecord


class IFLR(LogicalRecord):
    """Model an Indirectly Formatted Logical Record.

    This type of logical record is mainly mean for numerical data.

    This is an abstract base class; see its subclasses (FrameData and NoFormatFrameData) for final implementations.
    """

    logical_record_type: IFLRType   #: int-enum denoting type of the EFLR
    is_eflr = False                 #: indication that this is an indirectly formatted LR

    def __init__(self) -> None:
        """Initialise an IFLR."""

        super().__init__()
