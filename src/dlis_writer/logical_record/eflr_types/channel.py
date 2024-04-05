import logging
from typing import Union, Optional, Any, Self
import numpy as np
from h5py import Dataset  # type: ignore  # untyped library

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem, DimensionedItem
from dlis_writer.logical_record.eflr_types.axis import AxisSet
from dlis_writer.logical_record.eflr_types.long_name import LongNameSet
from dlis_writer.utils.internal_enums import RepresentationCode as RepC, EFLRType
from dlis_writer.utils.enums import Unit
from dlis_writer.utils.converters import ReprCodeConverter
from dlis_writer.utils.types import numpy_dtype_type
from dlis_writer.logical_record.core.attribute import (Attribute, DimensionAttribute, EFLRAttribute, NumericAttribute,
                                                       IdentAttribute, EFLROrTextAttribute, PropertiesAttribute)
from dlis_writer.utils.source_data_wrappers import SourceDataWrapper

logger = logging.getLogger(__name__)


class ReprCodeAttribute(Attribute):
    def __init__(self, parent_eflr: Optional[EFLRItem] = None) -> None:
        super().__init__('representation_code', converter=self.no_set, representation_code=RepC.USHORT,
                         parent_eflr=parent_eflr)

    def no_set(self, rc: Any) -> None:
        """Do not allow setting repr code of channel directly."""

        raise RuntimeError("Representation code of channel should not be set directly. Set `cast_dtype` instead.")

    def set_from_dtype(self, dt: Union[numpy_dtype_type, None]) -> None:
        if dt is None:
            self._value = None
        else:
            self._value = ReprCodeConverter.determine_repr_code_from_numpy_dtype(dt)

    def copy(self) -> Self:
        return self.__class__()


class ChannelItem(EFLRItem, DimensionedItem):
    """Model an object being part of Channel EFLR."""

    parent: "ChannelSet"

    def __init__(self, name: str, parent: "ChannelSet", dataset_name: Optional[str] = None,
                 cast_dtype: Optional[numpy_dtype_type] = None, **kwargs: Any) -> None:
        """Initialise ChannelItem.

        Args:
            name            :   Name of the ChannelItem.
            parent          :   Parent ChannelSet of this ChannelItem.
            dataset_name    :   Name of the data corresponding to this channel in the SourceDataWrapper.
            cast_dtype      :   Numpy data type the channel data should be cast to.
            **kwargs        :   Values of to be set as characteristics of the ChannelItem Attributes.
        """

        # need the attribute defined for representation code check
        self._cast_dtype: Union[numpy_dtype_type, None] = None

        self.long_name = EFLROrTextAttribute('long_name', object_class=LongNameSet)
        self.properties = PropertiesAttribute('properties')
        self.representation_code = ReprCodeAttribute(parent_eflr=self)
        self.units = IdentAttribute('units', converter=Unit.make_converter("units", soft=True, allow_none=True))
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=AxisSet, multivalued=True)
        self.element_limit = DimensionAttribute('element_limit')
        self.source = Attribute('source', representation_code=RepC.OBJREF)
        self.minimum_value = NumericAttribute('minimum_value', representation_code=RepC.FDOUBL, multivalued=True)
        self.maximum_value = NumericAttribute('maximum_value', representation_code=RepC.FDOUBL, multivalued=True)

        super().__init__(name, parent=parent, **kwargs)

        self._dataset_name: Union[str, None] = dataset_name
        self._set_cast_dtype(cast_dtype)

    @property
    def dataset_name(self) -> str:
        """Name of the data corresponding to this channel in the SourceDataWrapper."""

        return self._dataset_name if self._dataset_name is not None else self.name

    @dataset_name.setter
    def dataset_name(self, name: str) -> None:
        """Set a new dataset name."""

        self._dataset_name = name

    @property
    def cast_dtype(self) -> Union[numpy_dtype_type, None]:
        """Numpy data type the channel data will be cast to."""

        return self._cast_dtype

    @cast_dtype.setter
    def cast_dtype(self, dt: Union[numpy_dtype_type, None]) -> None:
        """Set or remove channel cast dtype."""

        self._set_cast_dtype(dt)

    def _set_cast_dtype(self, dt: Union[numpy_dtype_type, None]) -> None:
        if dt is not None:
            ReprCodeConverter.validate_numpy_dtype(dt)

        self._cast_dtype = dt
        self.representation_code.set_from_dtype(self.cast_dtype)

    def set_dimension_and_repr_code_from_data(self, data: SourceDataWrapper) -> None:
        """Determine and dimension and representation code attributes of the ChannelItem based on the source data."""

        sub_data = data[self.name]
        self._set_dimension_from_data(sub_data)
        self._set_repr_code_from_data(sub_data)

    def _set_dimension_from_data(self, sub_data: Union[np.ndarray, Dataset]) -> None:
        """Determine dimension (and element limit) of the Channel data from a relevant subset of a SourceDataWrapper."""

        dim = list(sub_data.shape[1:]) or [1]

        if self.dimension.value != dim:
            if self.dimension.value:
                raise RuntimeError(f"Previously defined dimension of {self}: {self.dimension.value} "
                                   f"does not match the dimension from data: {dim}")
            logger.debug(f"Setting dimension of {self} to {dim}")
            self.dimension.value = dim

        if self.element_limit.value != dim:
            if self.element_limit.value:  # was specified and is not exactly equal to dim
                if not self._compare_element_limit_vs_dimension(self.element_limit.value, dim):
                    # the difference is and not acceptable according to RP66 rules
                    raise RuntimeError(f"Previously defined element limit of {self}: {self.element_limit.value} "
                                       f"does not match the dimension from data: {dim}")
            else:
                # only set the element limit if it was None before
                logger.debug(f"Setting element limit of {self} to {dim}")
            self.element_limit.value = dim

    @staticmethod
    def _compare_element_limit_vs_dimension(el: list[int], dim: list[int]) -> bool:
        """Return True if the provided element limit is valid for the specified dimension, False otherwise.

        From RP66:
        'The ELEMENT-LIMIT Attribute specifies limits on the dimensionality and size of a Channel sample.
        The Count of this Attribute specifies the maximum allowable number of dimensions, and each Element of this
        Attribute specifies the maximum allowable size of the corresponding dimension in array elements.
        For example, if Element-Limit = {5 10 50}, then a Channel sample may have 0, 1, 2, or 3 dimensions.
        The first dimension size may be no larger than 5 elements, the second no larger than 10 elements, and the last
        no larger than 50 elements. Within these limits, the Channel sample may be of arbitrary size as specified
        by the Dimension Attribute (...).'
        """

        if len(el) < len(dim):
            return False

        for i in range(len(dim)):
            if el[i] < dim[i]:
                return False

        return True

    def _set_repr_code_from_data(self, sub_data: Union[np.ndarray, Dataset]) -> None:
        """Determine representation code of the Channel data from a relevant subset of a SourceDataWrapper."""

        dt = sub_data.dtype

        if self.cast_dtype is not None:
            if dt != self.cast_dtype:
                logger.warning(f"Data will be cast from {dt} to {self.cast_dtype}")
            return

        self._set_cast_dtype(dt)

    def _run_checks_and_set_defaults(self) -> None:
        """Set up default values of ChannelItem parameters if not explicitly set previously."""

        if not self.element_limit.value and self.dimension.value:
            logger.debug(f"Setting element limit of channel '{self.name}' to the same value "
                         f"as dimension: {self.dimension.value}")
            self.element_limit.value = self.dimension.value

        elif not self.dimension.value and self.element_limit.value:
            logger.debug(f"Setting dimension of channel '{self.name}' to the same value "
                         f"as element limit: {self.element_limit.value}")
            self.dimension.value = self.element_limit.value

        elif self.element_limit.value != self.dimension.value:
            if not self._compare_element_limit_vs_dimension(self.element_limit.value, self.dimension.value):
                # difference is not acceptable according to RP66 rules
                raise RuntimeError(f"For channel '{self.name}', dimension is {self.dimension.value} "
                                   f"and element limit is {self.element_limit.value}")

        self._check_axis_vs_dimension()

        if not self.long_name.value:
            logger.debug(f"Long name of channel '{self.name}' not specified; setting it to to the channel's name")
            self.long_name.value = self.name


class ChannelSet(EFLRSet):
    """Model Channel EFLR."""

    set_type = 'CHANNEL'
    logical_record_type = EFLRType.CHANNL
    item_type = ChannelItem


ChannelItem.parent_eflr_class = ChannelSet
