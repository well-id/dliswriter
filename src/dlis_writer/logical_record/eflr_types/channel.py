import logging
from typing import Union, Optional, Any, Self
import numpy as np
from h5py import Dataset    # type: ignore  # untyped library

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.logical_record.eflr_types.axis import AxisSet
from dlis_writer.utils.enums import RepresentationCode as RepC, EFLRType, UNITS
from dlis_writer.utils.converters import ReprCodeConverter, numpy_dtype_type
from dlis_writer.logical_record.core.attribute import (Attribute, DimensionAttribute, EFLRAttribute, NumericAttribute,
                                                       TextAttribute, IdentAttribute)
from dlis_writer.utils.source_data_wrappers import SourceDataWrapper


logger = logging.getLogger(__name__)


class ReprCodeAttribute(Attribute):
    def __init__(self, parent_eflr: Optional[Union[EFLRSet, EFLRItem]] = None) -> None:
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


class ChannelItem(EFLRItem):
    """Model an object being part of Channel EFLR."""

    parent: "ChannelSet"

    def __init__(self, name: str, dataset_name: Optional[str] = None, cast_dtype: Optional[numpy_dtype_type] = None,
                 **kwargs: Any) -> None:
        """Initialise ChannelItem.

        Args:
            name            :   Name of the ChannelItem.
            dataset_name    :   Name of the data corresponding to this channel in the SourceDataWrapper.
            cast_dtype      :   Numpy data type the channel data should be cast to.
            **kwargs        :   Values of to be set as characteristics of the ChannelItem Attributes.
        """

        self._cast_dtype = None  # need the attribute defined for representation code check

        self.long_name = TextAttribute('long_name')
        self.properties = IdentAttribute('properties', multivalued=True)
        self.representation_code = ReprCodeAttribute(parent_eflr=self)
        self.units = IdentAttribute('units', converter=self.convert_unit)
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=AxisSet, multivalued=True)
        self.element_limit = DimensionAttribute('element_limit')
        self.source = Attribute('source', representation_code=RepC.OBJREF)
        self.minimum_value = NumericAttribute('minimum_value', representation_code=RepC.FDOUBL, multivalued=True)
        self.maximum_value = NumericAttribute('maximum_value', representation_code=RepC.FDOUBL, multivalued=True)

        super().__init__(name, **kwargs)

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
                logger.warning(f"Previously defined dimension of {self}: {self.dimension.value} "
                               f"does not match the dimension from data: {dim}")
            logger.debug(f"Setting dimension of {self} to {dim}")
            self.dimension.value = dim

        if self.element_limit.value != dim:
            if self.element_limit.value:
                logger.warning(f"Previously defined element limit of {self}: {self.element_limit.value} "
                               f"does not match the dimension from data: {dim}")
            logger.debug(f"Setting element limit of {self} to {dim}")
            self.element_limit.value = dim

    def _set_repr_code_from_data(self, sub_data: Union[np.ndarray, Dataset]) -> None:
        """Determine representation code of the Channel data from a relevant subset of a SourceDataWrapper."""

        dt = sub_data.dtype

        if self.cast_dtype is not None:
            if dt != self.cast_dtype:
                logger.warning(f"Data will be cast from {dt} to {self.cast_dtype}")
            return

        self._set_cast_dtype(dt)

    def _set_defaults(self) -> None:
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
            logger.warning(f"For channel '{self.name}', dimension is {self.dimension.value} "
                           f"and element limit is {self.element_limit.value}")

        if not self.long_name.value:
            logger.debug(f"Long name of channel '{self.name}' not specified; setting it to to the channel's name")
            self.long_name.value = self.name

    @staticmethod
    def convert_unit(unit: Union[str, None]) -> Union[str, None]:
        """Check that unit is one of the values allowed by the standard (or None)."""

        if unit is None:
            return None

        if not isinstance(unit, str):
            raise TypeError(f"Expected a str, got {type(unit)}: {unit}")
        if unit not in UNITS:
            logger.warning(f"'{unit}' is not one of the allowed units")

        return unit


class ChannelSet(EFLRSet):
    """Model Channel EFLR."""

    set_type = 'CHANNEL'
    logical_record_type = EFLRType.CHANNL
    item_type = ChannelItem


ChannelItem.parent_eflr_class = ChannelSet
