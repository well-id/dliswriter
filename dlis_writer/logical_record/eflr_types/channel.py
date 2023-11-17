import logging
import numpy as np

from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.logical_record.eflr_types.axis import Axis
from dlis_writer.utils.enums import RepresentationCode as RepC, EFLRType, UNITS
from dlis_writer.utils.converters import ReprCodeConverter
from dlis_writer.logical_record.core.attribute import Attribute, DimensionAttribute, EFLRAttribute, NumericAttribute
from dlis_writer.utils.source_data_objects import HDF5Interface, SourceDataObject


logger = logging.getLogger(__name__)


class ChannelObject(EFLRObject):

    def __init__(self, name, parent: "Channel", dataset_name: str = None, **kwargs):

        self.long_name = Attribute('long_name', representation_code=RepC.ASCII, parent_eflr=self)
        self.properties = Attribute(
            'properties', representation_code=RepC.IDENT, multivalued=True, parent_eflr=self)
        self.representation_code = Attribute(
            'representation_code', converter=self.convert_repr_code, representation_code=RepC.USHORT, parent_eflr=self)
        self.units = Attribute(
            'units', converter=self.convert_unit, representation_code=RepC.IDENT, parent_eflr=self)
        self.dimension = DimensionAttribute('dimension', parent_eflr=self)
        self.axis = EFLRAttribute('axis', object_class=Axis, multivalued=True, parent_eflr=self)
        self.element_limit = DimensionAttribute('element_limit', parent_eflr=self)
        self.source = Attribute('source', representation_code=RepC.OBJREF, parent_eflr=self)
        self.minimum_value = NumericAttribute(
            'minimum_value', representation_code=RepC.FDOUBL, multivalued=True, parent_eflr=self)
        self.maximum_value = NumericAttribute(
            'maximum_value', representation_code=RepC.FDOUBL, multivalued=True, parent_eflr=self)

        self._dataset_name: str = dataset_name

        super().__init__(name, parent, **kwargs)

        self.set_defaults()

    @property
    def dataset_name(self):
        return self._dataset_name if self._dataset_name is not None else self.name

    @dataset_name.setter
    def dataset_name(self, name: str):
        self._dataset_name = name

    def set_dimension_and_repr_code_from_data(self, data: SourceDataObject):

        sub_data = data[self.dataset_name]
        self._set_dimension_from_data(sub_data)
        self._set_repr_code_from_data(sub_data)

    def _set_dimension_from_data(self, sub_data):
        rep = f"Channel '{self.name}'"

        dim = list(sub_data.shape[1:]) or [1]

        if self.dimension.value != dim:
            if self.dimension.value:
                logger.warning(f"Previously defined dimension of {rep}: {self.dimension.value} "
                               f"does not match the dimension from data: {dim}")
            logger.debug(f"Setting dimension of {rep} to {dim}")
            self.dimension.value = dim

        if self.element_limit.value != dim:
            if self.element_limit.value:
                logger.warning(f"Previously defined element limit of {rep}: {self.element_limit.value} "
                               f"does not match the dimension from data: {dim}")
            logger.debug(f"Setting element limit of {rep} to {dim}")
            self.element_limit.value = dim

    def _set_repr_code_from_data(self, sub_data):
        rep = f"Channel '{self.name}'"
        dt = sub_data.dtype

        suggested_rc = ReprCodeConverter.numpy_dtypes.get(dt.name, None)
        current_rc = self.representation_code.value

        if suggested_rc is None:
            if not current_rc:
                raise RuntimeError(f"Could not automatically convert dtype '{dt}' to a representation code; "
                                   f"please specify the representation code for {rep} manually")
            return

        if current_rc:
            if suggested_rc is not current_rc:
                logger.warning(f"Representation code for {rep} is {current_rc.name}, but according to the data "
                               f"it should be {suggested_rc.name}")
        else:
            logger.debug(f"Setting representation code of {rep} to {suggested_rc.name}")
            self.representation_code.value = suggested_rc

    def set_defaults(self):

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
    def convert_unit(unit):
        if unit is None:
            return None

        if not isinstance(unit, str):
            raise TypeError(f"Expected a str, got {type(unit)}: {unit}")
        if unit not in UNITS:
            raise ValueError(f"'{unit}' is not one of the allowed units")

        return unit

    @staticmethod
    def convert_repr_code(rc):
        return RepC.get_member(rc, allow_none=True)


class Channel(EFLR):
    set_type = 'CHANNEL'
    logical_record_type = EFLRType.CHANNL
    object_type = ChannelObject
