"""From RP66:
'A Frame constitutes the Indirectly Formatted Data of a Type FDATA Indirectly Formatted Logical Record (IFLR).
The Data Descriptor Reference of the FDATA Logical Record refers to a Frame Object (...)
and defines the Frame Type of the Frame.
Frames of a given Frame Type occur in sequences within a single Logical File.
A Frame is segmented into a Frame Number, followed by a fixed number of Slots that contain Channel samples,
one sample per Slot. The Frame Number is an integer (Representation Code UVARI) specifying the numerical order
of the Frame in the Frame Type, counting sequentially from one. All Frames of a given Frame Type record the same
Channels in the same order. The IFLRs containing Frames of a given Type need not be contiguous.

A Frame Type may or may not have an Index Channel. If there is an Index Channel, then it must appear first in the Frame
and it must be scalar. When an Index Channel is present, then all Channels in the Frame are assumed to be "sampled at"
the Index value. For example, if the Index is depth, then Channels are sampled at the given depth; if time, then they
are sampled at the given time, etc. (...)

The truth of the assumption just stated is relative to the measuring and recording system used and does not imply
absolute accuracy. For example, depth may be measured by a device that monitors cable movement at the surface,
which may differ from actual tool movement in the borehole. Corrections that are applied to Channels to improve
the accuracy of measurements or alignments to indices are left to the higher-level semantics of applications.

When there is no Index Channel, then Frames are implicitly indexed by Frame Number.'
"""

import logging
import numpy as np
from typing import Union, Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.eflr_types.channel import ChannelSet, ChannelItem
from dlis_writer.logical_record.core.attribute import (Attribute, EFLRAttribute, NumericAttribute, TextAttribute,
                                                       IdentAttribute)
from dlis_writer.utils.source_data_wrappers import SourceDataWrapper


logger = logging.getLogger(__name__)


class FrameItem(EFLRItem):
    """Model an object being part of Frame EFLR."""

    parent: "FrameSet"

    #: values for frame index type allowed by the standard
    frame_index_types = (
        'ANGULAR-DRIFT',
        'BOREHOLE-DEPTH',
        'NON-STANDARD',
        'RADIAL-DRIFT',
        'VERTICAL-DEPTH'
    )

    def __init__(self, name: str, parent: "FrameSet", **kwargs: Any) -> None:
        """Initialise FrameItem.

        Args:
            name        :   Name of the FrameItem.
            parent      :   Parent FrameSet of this FrameItem.
            **kwargs    :   Values of to be set as characteristics of the FrameItem Attributes.
        """

        self.description = TextAttribute('description')
        self.channels = EFLRAttribute('channels', object_class=ChannelSet, multivalued=True)
        self.index_type = IdentAttribute('index_type', converter=self.parse_index_type)
        self.direction = IdentAttribute('direction')
        self.spacing = NumericAttribute('spacing')
        self.encrypted = NumericAttribute(
            'encrypted', converter=self.convert_encrypted, representation_code=RepC.USHORT)
        self.index_min = NumericAttribute('index_min')
        self.index_max = NumericAttribute('index_max')

        super().__init__(name, parent=parent, **kwargs)

    @classmethod
    def parse_index_type(cls, value: str) -> str:
        """Check that the provided index type value is allowed by the standard. If not, issue a warning in the logs.

        Return the value as-is, unchanged.
        """

        if value not in cls.frame_index_types:
            logger.warning(f"Frame index type should be one of the following: "
                           f"'{', '.join(cls.frame_index_types)}'; got '{value}'")
        return value

    @staticmethod
    def convert_encrypted(value: Union[str, int, float, bool]) -> int:
        """Convert a provided 'encrypted' attribute value to an integer flag (0 or 1)."""

        if isinstance(value, bool):
            return int(value)
        if isinstance(value, str):
            if value.lower() in ('1', 'true', 't', 'yes', 'y'):
                return 1
            elif value.lower() in ('0', 'false', 'f', 'no', 'n'):
                return 0
            else:
                raise ValueError(f"Couldn't evaluate the boolean meaning of '{value}'")
        if isinstance(value, (int, float)):
            if value != 1 and value != 0:
                raise ValueError(f"Expected a 0 or a 1; got {value}")
            return int(value)
        else:
            raise TypeError(f"Cannot convert {type(value)} object ({value}) to integer")

    def setup_from_data(self, data: SourceDataWrapper) -> None:
        """Set up attributes of the frame and its channels based on the source data."""

        if not self.channels.value:
            raise RuntimeError(f"No channels defined for {self}")

        for channel in self.channels.value:
            channel.set_dimension_and_repr_code_from_data(data)

        self._setup_frame_params_from_data(data)

    def _setup_frame_params_from_data(self, data: SourceDataWrapper) -> None:
        """Set up the index characteristics of the frame based on the source data.

        The index characteristics include: min and max value, spacing, and direction (increasing/decreasing).

        This method assumes that the first channel added to the frame is the index channel.
        This assumption is frequently made in DLIS readers.
        """

        def assign_if_none(attr: Attribute, value: Any, key: str = 'value') -> None:
            """Check if an attribute part has already been assigned. If not, assign it to the provided value.

            Args:
                attr    :   Attribute instance whose part should be assigned a value.
                value   :   Value to be assigned to the attribute part, if no value has been assigned so far.
                key     :   Name of the part of attribute which should be assigned.
            """

            if getattr(attr, key) is None and value is not None:
                setattr(attr, key, value)

        index_channel: ChannelItem = self.channels.value[0]
        index_data = data[index_channel.name][:]
        unit = index_channel.units.value
        repr_code = index_channel.representation_code.value or RepC.FDOUBL
        spacing = np.median(np.diff(index_data))

        assign_if_none(index_channel.representation_code, repr_code)
        assign_if_none(self.index_min, index_data.min())
        assign_if_none(self.index_max, index_data.max())
        assign_if_none(self.spacing, spacing)
        assign_if_none(self.direction, 'INCREASING' if spacing > 0 else 'DECREASING')

        for at in (self.index_min, self.index_max, self.spacing):
            assign_if_none(at, key='units', value=unit)

    @property
    def channel_name_mapping(self) -> dict:
        return {ch.name: ch.dataset_name for ch in self.channels.value}

    @property
    def known_channel_dtypes_mapping(self) -> dict:
        return {ch.name: ch.cast_dtype for ch in self.channels.value if ch.cast_dtype is not None}


class FrameSet(EFLRSet):
    """Model Frame EFLR."""

    set_type = 'FRAME'
    logical_record_type = EFLRType.FRAME
    item_type = FrameItem


FrameItem.parent_eflr_class = FrameSet
