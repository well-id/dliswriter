import logging
import numpy as np
from typing import Union, Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.utils.internal.internal_enums import EFLRType, RepresentationCode as RepC
from dliswriter.utils.enums import FrameIndexType
from dliswriter.logical_record.eflr_types.channel import ChannelSet, ChannelItem
from dliswriter.logical_record.core.attribute import (Attribute, EFLRAttribute, NumericAttribute, TextAttribute,
                                                      IdentAttribute)
from dliswriter.utils.source_data_wrappers import SourceDataWrapper
from dliswriter.configuration import global_config


logger = logging.getLogger(__name__)


class FrameItem(EFLRItem):
    """Model an object being part of Frame EFLR."""

    parent: "FrameSet"

    def __init__(self, name: str, parent: "FrameSet", **kwargs: Any) -> None:
        """Initialise FrameItem.

        Args:
            name        :   Name of the FrameItem.
            parent      :   Parent FrameSet of this FrameItem.
            **kwargs    :   Values of to be set as characteristics of the FrameItem Attributes.
        """

        self.description = TextAttribute('description')
        self.channels = EFLRAttribute('channels', object_class=ChannelSet, multivalued=True)
        self.index_type = IdentAttribute(
            'index_type',
            converter=FrameIndexType.make_converter("index types", soft=True)
        )
        self.direction = IdentAttribute('direction')
        self.spacing = NumericAttribute('spacing')
        self.encrypted = NumericAttribute(
            'encrypted', converter=self.convert_encrypted, representation_code=RepC.USHORT)
        self.index_min = NumericAttribute('index_min')
        self.index_max = NumericAttribute('index_max')

        super().__init__(name, parent=parent, **kwargs)

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
                logger.debug(f"Setting {attr.label}.{key} of {self} to {value}")
                setattr(attr, key, value)

        index_channel: ChannelItem = self.channels.value[0]
        index_data = data[index_channel.name][:]

        if self.index_type.value is None:
            # according to RP66, if index_type is None:
            #   - spacing and direction are meaningless - b ut some viewer software need a spacing defined
            #   - there is no index channel, so index_min and index_max should be frame-data numbers (row numbers)
            logger.info(f"No index channel defined for {self}; it will be indexed by the row number")
            assign_if_none(self.spacing, 1)
            assign_if_none(self.index_min, 1)
            assign_if_none(self.index_max, index_data.shape[0])

        else:
            assign_if_none(self.index_min, index_data.min())
            assign_if_none(self.index_max, index_data.max())
            for at in (self.index_min, self.index_max, self.spacing):
                assign_if_none(at, key='units', value=index_channel.units.value)

            if index_data.ndim != 1:
                raise RuntimeError(f"Index channel's data must be 1-dimensional; got {index_data.ndim} dimensions "
                                   f"for {index_channel} of {self}")
            spacing, direction = self._compute_spacing_and_direction(index_data)

            if spacing is None:
                # spacing cannot be used because it is not uniform enough; using only direction - if available
                m = (f"Spacing of the index channel of {self} is not uniform; this can cause issues in some viewer "
                     f"software. Consider implicit indexing by row number number instead "
                     f"by removing frame index_type specification.")
                if global_config.high_compat_mode:
                    raise RuntimeError(m)
                logger.warning(m)
                if direction is not None:
                    assign_if_none(self.direction, 'INCREASING' if direction > 0 else 'DECREASING')
            else:
                assign_if_none(self.spacing, spacing)
                # no need to define direction if spacing is defined

    @staticmethod
    def _compute_spacing_and_direction(index_data: np.ndarray) -> tuple[Union[int, float, None], Union[bool, None]]:
        """Compute spacing and direction of the data.

        Note:
            If spacing is not uniform enough, it is assigned to None.
            If direction cannot be determined, it is assigned to None.
        """

        diff = np.diff(index_data)
        diff_unique = np.unique(diff)

        if (diff_unique == 0).all():
            direction = None  # all zeros ->not determined
        elif (diff_unique >= 0).all():
            direction = True  # all non-negative, at least one positive -> increasing
        elif (diff_unique <= 0).all():
            direction = False  # all non-positive, at least one negative -> decreasing
        else:
            direction = None  # some increasing, some decreasing -> not determined

        if len(diff_unique) == 1:
            # if spacing between each sample is the same, this is it
            return diff_unique[0], direction

        # if not, check if these are minor deviations (can be attributed to numerical accuracy) or not
        median_diff = np.median(diff).item()  # mypy complains that median_diff is a numpy array...
        if median_diff == 0:
            return None, direction  # need the median for denominator later; if it's 0, cannot determine uniformity

        deviations = (1 - diff_unique / median_diff) ** 2
        if (deviations < 0.001).all():  # if differences are small enough, median is representative for spacing
            return median_diff, direction

        # differences too big for spacing to be assumed uniform; set spacing to None
        return None, direction

    @property
    def channel_name_mapping(self) -> dict:
        """Mapping of names of channels of the frame on the names of the associated datasets."""

        return {ch.name: ch.dataset_name for ch in self.channels.value}

    @property
    def known_channel_dtypes_mapping(self) -> dict:
        """Mapping of names of channels of the frame on the data types, if explicitly defined."""

        return {ch.name: ch.cast_dtype for ch in self.channels.value if ch.cast_dtype is not None}


class FrameSet(EFLRSet):
    """Model Frame EFLR."""

    set_type = 'FRAME'
    logical_record_type = EFLRType.FRAME
    item_type = FrameItem


FrameItem.parent_eflr_class = FrameSet
