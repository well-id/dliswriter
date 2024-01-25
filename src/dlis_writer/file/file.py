from typing import Any, Union, Optional, TypeVar, Generator
import numpy as np
from timeit import timeit
from datetime import timedelta, datetime
import logging

from dlis_writer.utils.source_data_wrappers import DictDataWrapper, SourceDataWrapper
from dlis_writer.utils.types import (numpy_dtype_type, number_type, dtime_or_number_type, list_of_values_type,
                                     file_name_type, data_form_type, ListOrTuple, AttrDict)
from dlis_writer.utils.sized_generator import SizedGenerator
from dlis_writer.logical_record.core.eflr import EFLRItem, AttrSetup
from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.logical_record import eflr_types
from dlis_writer.logical_record.iflr_types.no_format_frame_data import NoFormatFrameData
from dlis_writer.file.multi_frame_data import MultiFrameData
from dlis_writer.file.writer import DLISWriter
from dlis_writer.file.eflr_sets_dict import EFLRSetsDict


logger = logging.getLogger(__name__)


T = TypeVar('T')
AttrSetupType = Union[T, AttrDict, AttrSetup]
OptAttrSetupType = Optional[AttrSetupType[T]]


class DLISFile:
    """Define the structure and contents of a DLIS and create a file based on the provided information."""

    def __init__(
            self,
            storage_unit_label: Optional[StorageUnitLabel] = None,
            file_header: Optional[eflr_types.FileHeaderItem] = None,
            set_identifier: str = "MAIN STORAGE UNIT",
            sul_sequence_number: int = 1,
            max_record_length: int = 8192,
            fh_identifier: str = "FILE HEADER",
            fh_sequence_number: int = 1
    ):
        """Initialise DLISFile.

        Args:
            storage_unit_label  :   An instance of StorageUnitLabel. If not provided, a new instance will be created
                                    based on other provided arguments and/or defaults.
            file_header         :   An instance of FileHeaderItem. If not provided, a new instance will be created
                                    based on other provided arguments and/or defaults.
            set_identifier      :   Used to create a StorageUnitLabel. ID of the storage set.
            sul_sequence_number :   Used to create a StorageUnitLabel. Indicates the order in which the current
                                    Storage Unit appears in a Storage Set.
            max_record_length   :   Used to create a StorageUnitLabel. Maximum length of each visible record.
                                    Cannot exceed 16384.
                                    See  # http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_5
            fh_identifier       :   Used to create a FileHeaderItem. Name identifying the FH instance.
            fh_sequence_number  :   Used to create a FileHeaderItem. Sequence number of the file.
        """

        self._sul: StorageUnitLabel = self._set_up_sul_or_fh(
            item_class=StorageUnitLabel,
            item=storage_unit_label,
            set_identifier=set_identifier,
            sequence_number=sul_sequence_number,
            max_record_length=max_record_length
        )

        file_header_item: eflr_types.FileHeaderItem = self._set_up_sul_or_fh(
            item_class=eflr_types.FileHeaderItem,
            item=file_header,
            identifier=fh_identifier,
            sequence_number=fh_sequence_number,
            parent=eflr_types.FileHeaderSet()
        )

        self._eflr_sets = EFLRSetsDict()
        self._eflr_sets.add_set(file_header_item.parent)

        self._data_dict: dict[str, np.ndarray] = {}
        self._max_dataset_copy = 1000

        self._no_format_frame_data: list[NoFormatFrameData] = []

    @staticmethod
    def _set_up_sul_or_fh(item_class: type[T], item: Optional[T], **kwargs: Any) -> T:

        if item is not None:
            if not isinstance(item, item_class):
                raise TypeError(f"Expected a {item_class.__name__}, got {type(item)}: {item}")
            logger.debug(f"Using the provided {item_class.__name__} instance")

        else:
            logger.debug(f"Creating a new {item_class.__name__} instance")
            item = item_class(**kwargs)

        logger.debug(f"{item_class.__name__} for the file: {repr(item)}")
        return item

    @property
    def storage_unit_label(self) -> StorageUnitLabel:
        """Storage Unit Label of the DLIS."""

        return self._sul

    @property
    def file_header(self) -> eflr_types.FileHeaderItem:
        """File header of the DLIS."""

        return list(self._eflr_sets.get_all_items_for_set_type(eflr_types.FileHeaderSet))[0]

    @property
    def defining_origin(self) -> Union[eflr_types.OriginItem, None]:
        """First Origin of the DLIS, describing the circumstances under which the file was created."""

        origins: list[eflr_types.OriginItem] = list(self._eflr_sets.get_all_items_for_set_type(eflr_types.OriginSet))
        return origins[0] if origins else None

    @property
    def default_origin_reference(self) -> Union[int, None]:
        if origin := self.defining_origin:
            return origin.file_set_number.value  # type: ignore  # this is an int or None, but mypy doesn't know
        return None

    @property
    def channels(self) -> list[eflr_types.ChannelItem]:
        """Channels defined for the DLIS."""

        return list(self._eflr_sets.get_all_items_for_set_type(eflr_types.ChannelSet))

    @property
    def frames(self) -> list[eflr_types.FrameItem]:
        """Frames defined for the DLIS."""

        return list(self._eflr_sets.get_all_items_for_set_type(eflr_types.FrameSet))

    def add_axis(
            self,
            name: str,
            axis_id: OptAttrSetupType[str] = None,
            coordinates: OptAttrSetupType[list_of_values_type] = None,
            spacing: OptAttrSetupType[number_type] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.AxisItem:
        """Define an axis (AxisObject) and add it to the DLIS.

        Args:
            name                :   Name of the axis.
            axis_id             :   ID of the axis.
            coordinates         :   List of coordinates of the axis.
            spacing             :   Spacing of the axis.
            set_name            :   Name of the AxisSet this axis should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.
        """

        ax = eflr_types.AxisItem(
            name=name,
            axis_id=axis_id,
            coordinates=coordinates,
            spacing=spacing,
            parent=self._eflr_sets.get_or_make_set(eflr_types.AxisSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return ax

    def add_calibration(
            self,
            name: str,
            calibrated_channels: OptAttrSetupType[ListOrTuple[eflr_types.ChannelItem]] = None,
            uncalibrated_channels: OptAttrSetupType[ListOrTuple[eflr_types.ChannelItem]] = None,
            coefficients: OptAttrSetupType[ListOrTuple[eflr_types.CalibrationCoefficientItem]] = None,
            measurements: OptAttrSetupType[ListOrTuple[eflr_types.CalibrationMeasurementItem]] = None,
            parameters: OptAttrSetupType[ListOrTuple[eflr_types.ParameterItem]] = None,
            method: OptAttrSetupType[str] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.CalibrationItem:
        """Define a calibration item and add it to the DLIS.

        Args:
            name                    :   Name of the calibration.
            calibrated_channels     :   Calibrated channels.
            uncalibrated_channels   :   Uncalibrated channels.
            coefficients            :   Coefficients of the calibration.
            measurements            :   Measurements made for the calibration.
            parameters              :   Parameters of the calibration.
            method                  :   Calibration method.
            set_name                :   Name of the CalibrationSet this calibration should be added to.
            origin_reference        :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured calibration object.
        """

        c = eflr_types.CalibrationItem(
            name=name,
            calibrated_channels=calibrated_channels,
            uncalibrated_channels=uncalibrated_channels,
            coefficients=coefficients,
            measurements=measurements,
            parameters=parameters,
            method=method,
            parent=self._eflr_sets.get_or_make_set(eflr_types.CalibrationSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return c

    def add_calibration_coefficient(
            self,
            name: str,
            label: OptAttrSetupType[str] = None,
            coefficients: OptAttrSetupType[list[number_type]] = None,
            references: OptAttrSetupType[list[number_type]] = None,
            plus_tolerances: OptAttrSetupType[list[number_type]] = None,
            minus_tolerances: OptAttrSetupType[list[number_type]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.CalibrationCoefficientItem:
        """Define a calibration coefficient object and add it to the DLIS.

        Args:
            name                :   Name of the calibration coefficient.
            label               :   Label of the calibration coefficient.
            coefficients        :   Coefficients of the item.
            references          :   References of the item.
            plus_tolerances     :   Plus tolerances of the item.
            minus_tolerances    :   Minus tolerances of the item.
            set_name            :   Name of the CorrelationCoefficientSet this item should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured calibration coefficient item.
        """

        c = eflr_types.CalibrationCoefficientItem(
            name=name,
            label=label,
            coefficients=coefficients,
            references=references,
            plus_tolerances=plus_tolerances,
            minus_tolerances=minus_tolerances,
            parent=self._eflr_sets.get_or_make_set(eflr_types.CalibrationCoefficientSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return c

    def add_calibration_measurement(
            self,
            name: str,
            phase: OptAttrSetupType[str] = None,
            measurement_source: OptAttrSetupType[eflr_types.ChannelItem] = None,
            measurement_type: OptAttrSetupType[str] = None,
            dimension: OptAttrSetupType[list[int]] = None,
            axis: OptAttrSetupType[eflr_types.AxisItem] = None,
            measurement: OptAttrSetupType[list[number_type]] = None,
            sample_count: OptAttrSetupType[int] = None,
            maximum_deviation: OptAttrSetupType[number_type] = None,
            standard_deviation: OptAttrSetupType[number_type] = None,
            begin_time: OptAttrSetupType[dtime_or_number_type] = None,
            duration: OptAttrSetupType[number_type] = None,
            reference: OptAttrSetupType[list[number_type]] = None,
            standard: OptAttrSetupType[list[number_type]] = None,
            plus_tolerance: OptAttrSetupType[list[number_type]] = None,
            minus_tolerance: OptAttrSetupType[list[number_type]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.CalibrationMeasurementItem:
        """Define a calibration measurement item and add it to the DLIS.

        Args:
            name                :   Name of the calibration measurement.
            phase               :   Phase of the measurement.
            measurement_source  :   Source of the measurement.
            measurement_type    :   Type of the measurement.
            dimension           :   Dimension of the measurement.
            axis                :   Axis of the measurement.
            measurement         :   Measured values.
            sample_count        :   Number of samples.
            maximum_deviation   :   Maximum deviation of the measurement.
            standard_deviation  :   Standard deviation of the measurement.
            begin_time          :   Start time of the measurement; date-time or number of seconds/minutes/etc.
                                    from a certain event.
            duration            :   Duration of the measurement.
            reference           :   Reference of the measurement.
            standard            :   Standard of the measurement.
            plus_tolerance      :   Plus tolerance of the measurement.
            minus_tolerance     :   Minus tolerance of the measurement.
            set_name            :   Name of the CorrelationMeasurementSet this measurement should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured CalibrationMeasurementItem instance.
        """

        m = eflr_types.CalibrationMeasurementItem(
            name=name,
            phase=phase,
            measurement_source=measurement_source,
            _type=measurement_type,
            dimension=dimension,
            axis=axis,
            measurement=measurement,
            sample_count=sample_count,
            maximum_deviation=maximum_deviation,
            standard_deviation=standard_deviation,
            begin_time=begin_time,
            duration=duration,
            reference=reference,
            standard=standard,
            plus_tolerance=plus_tolerance,
            minus_tolerance=minus_tolerance,
            parent=self._eflr_sets.get_or_make_set(eflr_types.CalibrationMeasurementSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return m

    def add_channel(
            self,
            name: str,
            data: Optional[np.ndarray] = None,
            dataset_name: Optional[str] = None,
            cast_dtype: Optional[numpy_dtype_type] = None,
            long_name: OptAttrSetupType[str] = None,
            dimension: OptAttrSetupType[Union[int, list[int]]] = None,
            element_limit: OptAttrSetupType[Union[int, list[int]]] = None,
            properties: OptAttrSetupType[list[str]] = None,
            units: OptAttrSetupType[str] = None,
            axis: OptAttrSetupType[eflr_types.AxisItem] = None,
            minimum_value: OptAttrSetupType[float] = None,
            maximum_value: OptAttrSetupType[float] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.ChannelItem:
        """Define a channel (ChannelItem) and add it to the DLIS.

        Args:
            name                :   Name of the channel.
            data                :   Data associated with the channel.
            dataset_name        :   Name of the data array associated with the channel in the data source provided
                                    at init of DLISFile.
            cast_dtype          :   Numpy data type the channel data should be cast to - e.g. np.float64, np.int32.
            long_name           :   Description of the channel.
            properties          :   List of properties of the channel.
            dimension           :   Dimension of the channel data. Determined automatically if not provided.
            element_limit       :   Element limit of the channel data. Determined automatically if not provided.
                                    Should be the same as dimension (in the current implementation of dlis_writer).
            units               :   Unit of the channel data.
            axis                :   Axis associated with the channel.
            minimum_value       :   Minimum value of the channel data.
            maximum_value       :   Maximum value of the channel data.
            set_name            :   Name of the ChannelSet this channel should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured ChannelObject instance, which is already added to the DLIS (but not to any frame).
        """

        if data is not None and not isinstance(data, np.ndarray):
            raise ValueError(f"Expected a numpy.ndarray, got a {type(data)}: {data}")

        dataset_name = self._get_unique_dataset_name(channel_name=name, dataset_name=dataset_name)

        ch = eflr_types.ChannelItem(
            name,
            long_name=long_name,
            dataset_name=dataset_name,
            cast_dtype=cast_dtype,
            properties=properties,
            dimension=dimension,
            element_limit=element_limit,
            units=units,
            axis=axis,
            minimum_value=minimum_value,
            maximum_value=maximum_value,
            parent=self._eflr_sets.get_or_make_set(eflr_types.ChannelSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )
        # skipping dimension and element limit because they will be determined from the data

        if data is not None:
            self._data_dict[ch.dataset_name] = data

        return ch

    def _get_unique_dataset_name(self, channel_name: str, dataset_name: Optional[str] = None) -> str:
        """Determine a unique name for channel's data in the internal data dict."""

        current_dataset_names = [ch.dataset_name for ch in self.channels]

        if dataset_name is not None:
            if dataset_name in current_dataset_names:
                raise ValueError(f"A data set with name '{dataset_name}' already exists")
            return dataset_name

        if channel_name not in current_dataset_names:
            return channel_name

        for i in range(1, self._max_dataset_copy):
            n = f"{channel_name}__{i}"
            if n not in current_dataset_names:
                break
        else:
            # loop not broken - all options exhausted
            raise RuntimeError(f"Cannot find a unique dataset name for channel '{channel_name}'")

        return n

    def add_comment(
            self, name: str,
            text: OptAttrSetupType[list[str]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.CommentItem:
        """Create a comment item and add it to the DLIS.

        Args:
            name                :   Name of the comment.
            text                :   Content of the comment.
            set_name            :   Name of the CommentSet this comment should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured comment item.
        """

        c = eflr_types.CommentItem(
            name=name,
            text=text,
            parent=self._eflr_sets.get_or_make_set(eflr_types.CommentSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return c

    def add_computation(
            self,
            name: str,
            long_name: OptAttrSetupType[str] = None,
            properties: OptAttrSetupType[list[str]] = None,
            dimension: OptAttrSetupType[list[int]] = None,
            axis: OptAttrSetupType[eflr_types.AxisItem] = None,
            zones: OptAttrSetupType[ListOrTuple[eflr_types.ZoneItem]] = None,
            values: OptAttrSetupType[list[number_type]] = None,
            source: OptAttrSetupType[EFLRItem] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.ComputationItem:
        """Create a computation item and add it to the DLIS.

        Args:
            name                :   Name of the computation.
            long_name           :   Description of the computation.
            properties          :   Properties of the computation.
            dimension           :   Dimension of the computation.
            axis                :   Axis associated with the computation.
            zones               :   Zones associated with the computation.
            values              :   Values of the computation.
            source              :   Source of the computation.
            set_name            :   Name of the ComputationSet this computation should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured computation item.
        """

        c = eflr_types.ComputationItem(
            name=name,
            long_name=long_name,
            properties=properties,
            dimension=dimension,
            axis=axis,
            zones=zones,
            values=values,
            source=source,
            parent=self._eflr_sets.get_or_make_set(eflr_types.ComputationSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return c

    def add_equipment(
            self,
            name: str,
            trademark_name: OptAttrSetupType[str] = None,
            status: OptAttrSetupType[int] = None,
            eq_type: OptAttrSetupType[str] = None,
            serial_number: OptAttrSetupType[str] = None,
            location: OptAttrSetupType[str] = None,
            height: OptAttrSetupType[number_type] = None,
            length: OptAttrSetupType[number_type] = None,
            minimum_diameter: OptAttrSetupType[number_type] = None,
            maximum_diameter: OptAttrSetupType[number_type] = None,
            volume: OptAttrSetupType[number_type] = None,
            weight: OptAttrSetupType[number_type] = None,
            hole_size: OptAttrSetupType[number_type] = None,
            pressure: OptAttrSetupType[number_type] = None,
            temperature: OptAttrSetupType[number_type] = None,
            vertical_depth: OptAttrSetupType[number_type] = None,
            radial_drift: OptAttrSetupType[number_type] = None,
            angular_drift: OptAttrSetupType[number_type] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.EquipmentItem:
        """Define an equipment object.

        Args:
            name                :   Name of the equipment.
            trademark_name      :   Trademark name.
            status              :   Status of the equipment: integer, 1 or 0.
            eq_type             :   Type of the equipment.
            serial_number       :   Serial number of the equipment.
            location            :   Location of the equipment.
            height              :   Height.
            length              :   Length.
            minimum_diameter    :   Maximum diameter.
            maximum_diameter    :   Minimum diameter.
            volume              :   Volume.
            weight              :   Weight of the equipment.
            hole_size           :   Hole size.
            pressure            :   Pressure.
            temperature         :   Temperature.
            vertical_depth      :   Vertical depth.
            radial_drift        :   Radial drift.
            angular_drift       :   Angular drift.
            set_name            :   Name of the EquipmentSet this equipment should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured EquipmentObject instance.
        """

        eq = eflr_types.EquipmentItem(
            name=name,
            trademark_name=trademark_name,
            status=status,
            _type=eq_type,
            serial_number=serial_number,
            location=location,
            height=height,
            length=length,
            minimum_diameter=minimum_diameter,
            maximum_diameter=maximum_diameter,
            volume=volume,
            weight=weight,
            hole_size=hole_size,
            pressure=pressure,
            temperature=temperature,
            vertical_depth=vertical_depth,
            radial_drift=radial_drift,
            angular_drift=angular_drift,
            parent=self._eflr_sets.get_or_make_set(eflr_types.EquipmentSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return eq

    def add_frame(
            self,
            name: str,
            channels: OptAttrSetupType[ListOrTuple[eflr_types.ChannelItem]],
            description: OptAttrSetupType[str] = None,
            index_type: OptAttrSetupType[str] = None,
            direction: OptAttrSetupType[str] = None,
            spacing: OptAttrSetupType[number_type] = None,
            encrypted: OptAttrSetupType[int] = None,
            index_min: OptAttrSetupType[number_type] = None,
            index_max: OptAttrSetupType[number_type] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.FrameItem:
        """Define a frame (FrameObject) and add it to the DLIS.

        Args:
            name                :   Name of the frame.
            channels            :   Channels associated with the frame.
            description         :   Description of the frame.
            index_type          :   Description of the type of data defining the frame index.
            direction           :   Indication of whether the index has increasing or decreasing values. Allowed values:
                                    'INCREASING', 'DECREASING'.
            spacing             :   Spacing between consecutive values in the frame index.
            encrypted           :   Indication whether the frame is encrypted (0 if not, 1 if yes).
            index_min           :   Minimum value of the frame index.
            index_max           :   Maximum value of the frame index.
            set_name            :   Name of the FrameSet this frame should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Note:
            Values: direction, spacing, index_min, and index_max are automatically determined if not provided.
            However, in some cases it might be beneficial - and more accurate - to explicitly specify these values.

        Returns:
            A configured FrameObject instance, added to the DLIS.
        """

        if not isinstance(channels, (list, tuple)):
            raise TypeError(f"Expected a list or tuple of channels, got {type(channels)}: {channels}")

        if not channels:
            raise ValueError("At least one channel must be specified for a frame")

        if not all(isinstance(c, eflr_types.ChannelItem) for c in channels):
            raise TypeError(f"Expected a list of ChannelObject instances; "
                            f"got types: {', '.join(str(type(c)) for c in channels)}")

        fr = eflr_types.FrameItem(
            name,
            channels=channels,
            description=description,
            index_type=index_type,
            direction=direction,
            spacing=spacing,
            encrypted=encrypted,
            index_min=index_min,
            index_max=index_max,
            parent=self._eflr_sets.get_or_make_set(eflr_types.FrameSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return fr

    def add_group(
            self,
            name: str,
            description: OptAttrSetupType[str] = None,
            object_type: OptAttrSetupType[str] = None,
            object_list: OptAttrSetupType[ListOrTuple[EFLRItem]] = None,
            group_list: OptAttrSetupType[ListOrTuple[eflr_types.GroupItem]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.GroupItem:
        """Create a group of EFLR items and add it to the DLIS.

        Args:
            name                :   Name of the group.
            description         :   Description of the group.
            object_type         :   Type of the objects contained in the group, e.g. CHANNEL, FRAME, PATH, etc.
            object_list         :   List of the EFLR items to be added to this group.
            group_list          :   List of group items to be added to this group.
            set_name            :   Name of the FrameSet this frame should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured group item.
        """

        g = eflr_types.GroupItem(
            name=name,
            description=description,
            object_type=object_type,
            object_list=object_list,
            group_list=group_list,
            parent=self._eflr_sets.get_or_make_set(eflr_types.GroupSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return g

    def add_long_name(
            self,
            name: str,
            general_modifier: OptAttrSetupType[list[str]] = None,
            quantity: OptAttrSetupType[str] = None,
            quantity_modifier: OptAttrSetupType[list[str]] = None,
            altered_form: OptAttrSetupType[str] = None,
            entity: OptAttrSetupType[str] = None,
            entity_modifier: OptAttrSetupType[list[str]] = None,
            entity_number: OptAttrSetupType[str] = None,
            entity_part: OptAttrSetupType[str] = None,
            entity_part_number: OptAttrSetupType[str] = None,
            generic_source: OptAttrSetupType[str] = None,
            source_part: OptAttrSetupType[list[str]] = None,
            source_part_number: OptAttrSetupType[list[str]] = None,
            conditions: OptAttrSetupType[list[str]] = None,
            standard_symbol: OptAttrSetupType[str] = None,
            private_symbol: Optional[str] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.LongNameItem:
        """Create a long name item and add it to the DLIS.

        Args:
            name                :   Name of the long name item.
            general_modifier    :   General modifier(s).
            quantity            :   Quantity.
            quantity_modifier   :   Quantity modifier(s).
            altered_form        :   Altered form.
            entity              :   Entity.
            entity_modifier     :   Entity modifier(s).
            entity_number       :   Entity number.
            entity_part         :   Entity part.
            entity_part_number  :   Entity part number.
            generic_source      :   Generic source.
            source_part         :   Source part(s).
            source_part_number  :   Source part number(s).
            conditions          :   Conditions.
            standard_symbol     :   Standard symbol.
            private_symbol      :   Private symbol.
            set_name            :   Name of the LongNameSet this long name item should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured long name item.
        """

        ln = eflr_types.LongNameItem(
            name=name,
            general_modifier=general_modifier,
            quantity=quantity,
            quantity_modifier=quantity_modifier,
            altered_form=altered_form,
            entity=entity,
            entity_modifier=entity_modifier,
            entity_number=entity_number,
            entity_part=entity_part,
            entity_part_number=entity_part_number,
            generic_source=generic_source,
            source_part=source_part,
            source_part_number=source_part_number,
            conditions=conditions,
            standard_symbol=standard_symbol,
            private_symbol=private_symbol,
            parent=self._eflr_sets.get_or_make_set(eflr_types.LongNameSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return ln

    def add_message(
            self,
            name: str,
            message_type: OptAttrSetupType[str] = None,
            time: OptAttrSetupType[dtime_or_number_type] = None,
            borehole_drift: OptAttrSetupType[number_type] = None,
            vertical_depth: OptAttrSetupType[number_type] = None,
            radial_drift: OptAttrSetupType[number_type] = None,
            angular_drift: OptAttrSetupType[number_type] = None,
            text: OptAttrSetupType[list[str]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.MessageItem:
        """Create a message and add it to DLIS.

        Args:
            name                :   Name of the message.
            message_type        :   Type of the message.
            time                :   Time of the message.
            borehole_drift      :   Borehole drift.
            vertical_depth      :   Vertical depth.
            radial_drift        :   Radial drift.
            angular_drift       :   Angular drift.
            text                :   Text of the message.
            set_name            :   Name of the MessageSet this message should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured message.
        """

        m = eflr_types.MessageItem(
            name=name,
            _type=message_type,
            time=time,
            borehole_drift=borehole_drift,
            vertical_depth=vertical_depth,
            radial_drift=radial_drift,
            angular_drift=angular_drift,
            text=text,
            parent=self._eflr_sets.get_or_make_set(eflr_types.MessageSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return m

    def add_no_format(
            self,
            name: str,
            consumer_name: OptAttrSetupType[str] = None,
            description: OptAttrSetupType[str] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.NoFormatItem:
        """Create a no-format item and add it to the DLIS.

        Args:
            name                :   Name of the no-format item.
            consumer_name       :   Consumer name.
            description         :   Description.
            set_name            :   Name of the NoFormatSet this item should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured no-format item.
        """

        nf = eflr_types.NoFormatItem(
            name=name,
            consumer_name=consumer_name,
            description=description,
            parent=self._eflr_sets.get_or_make_set(eflr_types.NoFormatSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return nf

    def add_no_format_frame_data(
            self,
            no_format_object: eflr_types.NoFormatItem,
            data: str
    ) -> NoFormatFrameData:
        """Create a no-format frame data object.

        Args:
            no_format_object    :   No-format item this data belongs to.
            data                :   Data associated with the object. Will be encoded as ASCII.

        Returns:
            A configured NoFormatFrameData instance.
        """

        d = NoFormatFrameData(no_format_object, data)

        self._no_format_frame_data.append(d)
        return d

    def add_origin(
            self,
            name: str,
            file_set_number: OptAttrSetupType[int] = None,
            file_set_name: OptAttrSetupType[str] = None,
            file_id: OptAttrSetupType[str] = None,
            file_number: OptAttrSetupType[int] = None,
            file_type: OptAttrSetupType[str] = None,
            product: OptAttrSetupType[str] = None,
            version: OptAttrSetupType[str] = None,
            programs: OptAttrSetupType[list[str]] = None,
            creation_time: OptAttrSetupType[Union[datetime, str]] = None,
            order_number: OptAttrSetupType[str] = None,
            descent_number: OptAttrSetupType[int] = None,
            run_number: OptAttrSetupType[int] = None,
            well_id: OptAttrSetupType[int] = None,
            well_name: OptAttrSetupType[str] = None,
            field_name: OptAttrSetupType[str] = None,
            producer_code: OptAttrSetupType[int] = None,
            producer_name: OptAttrSetupType[str] = None,
            company: OptAttrSetupType[str] = None,
            name_space_name: OptAttrSetupType[str] = None,
            name_space_version: OptAttrSetupType[int] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.OriginItem:
        """Create an origin.

        Args:
            name                :   Name of the parameter.
            file_set_number     :   File set number. Used as 'origin reference' in all other objects added to the file.
                                    If not specified, it is assigned randomly (in accordance with the RP66 specs).
            file_set_name       :   File set name.
            file_id             :   File ID.
            file_number         :   File number.
            file_type           :   File type.
            product             :   Product description.
            version             :   Version indicator.
            programs            :   List of programs.
            creation_time       :   Creation time.
            order_number        :   Order number.
            descent_number      :   Descent number.
            run_number          :   Run number.
            well_id             :   Well ID.
            well_name           :   Well name.
            field_name          :   Field name.
            producer_code       :   Producer code.
            producer_name       :   Producer name.
            company             :   Company name.
            name_space_name     :   Name space name.
            name_space_version  :   Name space version.
            set_name            :   Name of the OriginSet this origin should be added to.

        Returns:
            A configured OriginItem instance.
        """

        if self.defining_origin:
            raise RuntimeError("An OriginItem is already defined for the current DLISFile")

        o = eflr_types.OriginItem(
            name=name,
            file_set_number=file_set_number,
            file_set_name=file_set_name,
            file_id=file_id,
            file_number=file_number,
            file_type=file_type,
            product=product,
            version=version,
            programs=programs,
            creation_time=creation_time,
            order_number=order_number,
            descent_number=descent_number,
            run_number=run_number,
            well_id=well_id,
            well_name=well_name,
            field_name=field_name,
            producer_code=producer_code,
            producer_name=producer_name,
            company=company,
            name_space_name=name_space_name,
            name_space_version=name_space_version,
            parent=self._eflr_sets.get_or_make_set(eflr_types.OriginSet, set_name=set_name)
        )

        if len(list(self._eflr_sets.get_all_items_for_set_type(eflr_types.OriginSet))) == 1:
            ref = o.file_set_number.value
            logger.info(f"Assigning origin reference {ref} to all EFLR items without origin reference defined")

            for eflr_set_dict in self._eflr_sets.values():
                for eflr_set in eflr_set_dict.values():
                    for eflr_item in eflr_set.get_all_eflr_items():
                        if eflr_item.origin_reference is None:
                            eflr_item.origin_reference = ref

        return o

    def add_parameter(
            self,
            name: str,
            long_name: OptAttrSetupType[str] = None,
            dimension: OptAttrSetupType[list[int]] = None,
            axis: OptAttrSetupType[eflr_types.AxisItem] = None,
            zones: OptAttrSetupType[ListOrTuple[eflr_types.ZoneItem]] = None,
            values: OptAttrSetupType[list_of_values_type] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.ParameterItem:
        """Create a parameter.

        Args:
            name                :   Name of the parameter.
            long_name           :   Description of the parameter.
            dimension           :   Dimension of the parameter.
            axis                :   Axis associated with the parameter.
            zones               :   Zones the parameter is defined for.
            values              :   Values of the parameter - numerical or textual.
            set_name            :   Name of the ParameterSet this parameter should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured ParameterObject instance.
        """

        p = eflr_types.ParameterItem(
            name=name,
            long_name=long_name,
            dimension=dimension,
            axis=axis,
            zones=zones,
            values=values,
            parent=self._eflr_sets.get_or_make_set(eflr_types.ParameterSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return p

    def add_path(
            self,
            name: str,
            frame_type: OptAttrSetupType[eflr_types.FrameItem] = None,
            well_reference_point: OptAttrSetupType[eflr_types.WellReferencePointItem] = None,
            value: OptAttrSetupType[ListOrTuple[eflr_types.ChannelItem]] = None,
            borehole_depth: OptAttrSetupType[number_type] = None,
            vertical_depth: OptAttrSetupType[number_type] = None,
            radial_drift: OptAttrSetupType[number_type] = None,
            angular_drift: OptAttrSetupType[number_type] = None,
            time: OptAttrSetupType[number_type] = None,
            depth_offset: OptAttrSetupType[number_type] = None,
            measure_point_offset: OptAttrSetupType[number_type] = None,
            tool_zero_offset: OptAttrSetupType[number_type] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.PathItem:
        """Define a Path and add it to the DLIS.

        Args:
            name                    :   Name of the path.
            frame_type              :   Frame associated with the path.
            well_reference_point    :   Well reference of the path.
            value                   :   Channels associated with the path.
            borehole_depth          :   Borehole depth.
            vertical_depth          :   Vertical depth.
            radial_drift            :   Radial drift.
            angular_drift           :   Angular drift.
            time                    :   Time.
            depth_offset            :   Depth offset.
            measure_point_offset    :   Measure point offset.
            tool_zero_offset        :   Tool zero offset.
            set_name                :   Name of the PathSet this path should be added to.
            origin_reference        :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured Path instance.
        """

        p = eflr_types.PathItem(
            name=name,
            frame_type=frame_type,
            well_reference_point=well_reference_point,
            value=value,
            borehole_depth=borehole_depth,
            vertical_depth=vertical_depth,
            radial_drift=radial_drift,
            angular_drift=angular_drift,
            time=time,
            depth_offset=depth_offset,
            measure_point_offset=measure_point_offset,
            tool_zero_offset=tool_zero_offset,
            parent=self._eflr_sets.get_or_make_set(eflr_types.PathSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return p

    def add_process(
            self,
            name: str,
            description: OptAttrSetupType[str] = None,
            trademark_name: OptAttrSetupType[str] = None,
            version: OptAttrSetupType[str] = None,
            properties: OptAttrSetupType[list[str]] = None,
            status: OptAttrSetupType[str] = None,
            input_channels: OptAttrSetupType[ListOrTuple[eflr_types.ChannelItem]] = None,
            output_channels: OptAttrSetupType[ListOrTuple[eflr_types.ChannelItem]] = None,
            input_computations: OptAttrSetupType[ListOrTuple[eflr_types.ComputationItem]] = None,
            output_computations: OptAttrSetupType[ListOrTuple[eflr_types.ComputationItem]] = None,
            parameters: OptAttrSetupType[ListOrTuple[eflr_types.ParameterItem]] = None,
            comments: OptAttrSetupType[list[str]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.ProcessItem:
        """Define a process item and add it to DLIS.

        Args:
            name                :   Name of the process.
            description         :   Description of the process.
            trademark_name      :   Trademark name of the process.
            version             :   Version of the process.
            properties          :   Properties of the process.
            status              :   Status of the process; 1 or 0.
            input_channels      :   Channels serving as input for the process.
            output_channels     :   Channels serving as output for the process.
            input_computations  :   Input computations of the process.
            output_computations :   Output computations of the process.
            parameters          :   Parameters of the process.
            comments            :   Comments.
            set_name            :   Name of the ProcessSet this process should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured ProcessItem instance.
        """

        p = eflr_types.ProcessItem(
            name=name,
            description=description,
            trademark_name=trademark_name,
            version=version,
            properties=properties,
            status=status,
            input_channels=input_channels,
            output_channels=output_channels,
            input_computations=input_computations,
            output_computations=output_computations,
            parameters=parameters,
            comments=comments,
            parent=self._eflr_sets.get_or_make_set(eflr_types.ProcessSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return p

    def add_splice(
            self,
            name: str,
            output_channel: OptAttrSetupType[eflr_types.ChannelItem] = None,
            input_channels: OptAttrSetupType[ListOrTuple[eflr_types.ChannelItem]] = None,
            zones: OptAttrSetupType[ListOrTuple[eflr_types.ZoneItem]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.SpliceItem:
        """Create a splice object.

        Args:
            name                :   Name of the splice.
            output_channel      :   Output of the splice.
            input_channels      :   Input of the splice.
            zones               :   Zones the splice is defined for.
            set_name            :   Name of the SpliceSet this splice should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured splice.
        """

        sp = eflr_types.SpliceItem(
            name=name,
            output_channel=output_channel,
            input_channels=input_channels,
            zones=zones,
            parent=self._eflr_sets.get_or_make_set(eflr_types.SpliceSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return sp

    def add_tool(
            self,
            name: str,
            description: OptAttrSetupType[str] = None,
            trademark_name: OptAttrSetupType[str] = None,
            generic_name: OptAttrSetupType[str] = None,
            parts: OptAttrSetupType[ListOrTuple[eflr_types.EquipmentItem]] = None,
            status: OptAttrSetupType[int] = None,
            channels: OptAttrSetupType[ListOrTuple[eflr_types.ChannelItem]] = None,
            parameters: OptAttrSetupType[ListOrTuple[eflr_types.ParameterItem]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.ToolItem:
        """Create a tool object.

        Args:
            name                :   Name of the tool.
            description         :   Description of the tool.
            trademark_name      :   Trademark name.
            generic_name        :   Generic name.
            parts               :   Equipment this tool consists of.
            status              :   Status of the tool: 1 or 0.
            channels            :   Channels associated with this tool.
            parameters          :   Parameters associated with this tool.
            set_name            :   Name of the ToolSet this tool should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured tool.
        """

        t = eflr_types.ToolItem(
            name=name,
            description=description,
            trademark_name=trademark_name,
            generic_name=generic_name,
            parts=parts,
            status=status,
            channels=channels,
            parameters=parameters,
            parent=self._eflr_sets.get_or_make_set(eflr_types.ToolSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return t

    def add_well_reference_point(
            self,
            name: str,
            permanent_datum: OptAttrSetupType[str] = None,
            vertical_zero: OptAttrSetupType[str] = None,
            permanent_datum_elevation: OptAttrSetupType[number_type] = None,
            above_permanent_datum: OptAttrSetupType[number_type] = None,
            magnetic_declination: OptAttrSetupType[number_type] = None,
            coordinate_1_name: OptAttrSetupType[str] = None,
            coordinate_1_value: OptAttrSetupType[number_type] = None,
            coordinate_2_name: OptAttrSetupType[str] = None,
            coordinate_2_value: OptAttrSetupType[number_type] = None,
            coordinate_3_name: OptAttrSetupType[str] = None,
            coordinate_3_value: OptAttrSetupType[number_type] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.WellReferencePointItem:
        """Define a well reference point and add it to the DLIS.

        Args:
            name                        :   Name of the well reference point.
            permanent_datum             :   Permanent datum (name).
            vertical_zero               :   Vertical zero (name).
            permanent_datum_elevation   :   Elevation of the permanent datum.
            above_permanent_datum       :   Value above permanent datum.
            magnetic_declination        :   Magnetic declination.
            coordinate_1_name           :   Name of coordinate 1.
            coordinate_1_value          :   Value of coordinate 1.
            coordinate_2_name           :   Name of coordinate 2.
            coordinate_2_value          :   Value of coordinate 2.
            coordinate_3_name           :   Name of coordinate 3.
            coordinate_3_value          :   Value of coordinate 3.
            set_name                    :   Name of the WellReferencePointSet this item should be added to.
            origin_reference            :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured WellReferencePointItem instance.
        """

        w = eflr_types.WellReferencePointItem(
            name=name,
            permanent_datum=permanent_datum,
            vertical_zero=vertical_zero,
            permanent_datum_elevation=permanent_datum_elevation,
            above_permanent_datum=above_permanent_datum,
            magnetic_declination=magnetic_declination,
            coordinate_1_name=coordinate_1_name,
            coordinate_1_value=coordinate_1_value,
            coordinate_2_name=coordinate_2_name,
            coordinate_2_value=coordinate_2_value,
            coordinate_3_name=coordinate_3_name,
            coordinate_3_value=coordinate_3_value,
            parent=self._eflr_sets.get_or_make_set(eflr_types.WellReferencePointSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return w

    def add_zone(
            self,
            name: str,
            description: OptAttrSetupType[str] = None,
            domain: OptAttrSetupType[str] = None,
            maximum: OptAttrSetupType[dtime_or_number_type] = None,
            minimum: Optional[AttrSetupType[dtime_or_number_type]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.ZoneItem:
        """Create a zone (ZoneObject) and add it to the DLIS.

        Args:
            name                :   Name of the zone.
            description         :   Description of the zone.
            domain              :   Domain of the zone. One of: 'BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH'.
            maximum             :   Maximum of the zone.
            minimum             :   Minimum of the zone.
            set_name            :   Name of the ZoneSet this zone should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Note:
            Maximum and minimum should be instances of datetime.datetime if the domain is TIME. In other cases,
            they should be floats.

        Returns:
            A configured zone, added to the DLIS.
        """

        z = eflr_types.ZoneItem(
            name=name,
            description=description,
            domain=domain,
            maximum=maximum,
            minimum=minimum,
            parent=self._eflr_sets.get_or_make_set(eflr_types.ZoneSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

        return z

    def check_objects(self) -> None:
        """Check objects defined for the DLISFile. Called before writing the file."""

        self._check_completeness()
        self._check_channels_assigned_to_frames()

    def _check_completeness(self) -> None:
        """Check that the collection contains all required objects in the required (min/max) numbers.

        Raises:
            RuntimeError    :   If not enough or too many of any of the required object types are defined.
        """

        if not self.file_header:
            raise RuntimeError("No file header defined for the file")

        if len(list(self._eflr_sets.get_all_items_for_set_type(eflr_types.FileHeaderSet))) > 1:
            raise RuntimeError("Only one origin can be defined for the file")

        if not self.defining_origin:
            raise RuntimeError("No origin defined for the file")

        if not self.channels:
            raise RuntimeError("No channels defined for the file")

        if not self.frames:
            raise RuntimeError("No frames defined for the file")

    def _check_channels_assigned_to_frames(self) -> None:
        """Check that all defined ChannelObject instances are assigned to at least one FrameObject.

        Issues a warning in the logs if the condition is not fulfilled (possible issues with opening file in DeepView).
        """

        channels_in_frames = set()
        for frame_item in self.frames:
            channels_in_frames |= set(frame_item.channels.value)

        for channel_item in self.channels:
            if channel_item not in channels_in_frames:
                logger.warning(f"{channel_item} has not been added to any frame; "
                               f"this might cause issues with opening the produced DLIS file in some software")

    def _make_multi_frame_data(
            self,
            fr: eflr_types.FrameItem,
            data: Optional[data_form_type] = None,
            from_idx: int = 0,
            to_idx: Optional[int] = None,
            **kwargs: Any
    ) -> MultiFrameData:
        """Create a MultiFrameData object, containing the frame and associated data, generating FrameData instances."""

        data_object: SourceDataWrapper

        if data is None:
            data = {}

        if isinstance(data, dict):
            self._data_dict = self._data_dict | data
            data_object = DictDataWrapper(self._data_dict, mapping=fr.channel_name_mapping,
                                          known_dtypes=fr.known_channel_dtypes_mapping,
                                          from_idx=from_idx, to_idx=to_idx)
        else:
            if self._data_dict:
                raise TypeError(f"Expected a dictionary of np.ndarrays; got {type(data)}: {data} "
                                f"(Note: a dictionary is the only allowed type because some channels have been added"
                                f"with associated data arrays")
            data_object = SourceDataWrapper.make_wrapper(
                data, mapping=fr.channel_name_mapping, known_dtypes=fr.known_channel_dtypes_mapping,
                from_idx=from_idx, to_idx=to_idx
            )

        fr.setup_from_data(data_object)
        return MultiFrameData(fr, data_object, **kwargs)

    def generate_logical_records(self, chunk_size: Optional[int], data: Optional[data_form_type] = None,
                                 **kwargs: Any) -> SizedGenerator:
        """Iterate over all logical records defined in the file.

        Yields: EFLR and IFLR objects defined for the file.

        Note: Storage Unit Label should be added to the file separately before adding other records.
        """

        frame_items: Generator[eflr_types.FrameItem, None, None] \
            = self._eflr_sets.get_all_items_for_set_type(eflr_types.FrameSet)
        multi_frame_data_objects: list[MultiFrameData] = [
            self._make_multi_frame_data(fr, chunk_size=chunk_size, data=data, **kwargs) for fr in frame_items
        ]

        n = 0
        for eflr_set_type in self._eflr_sets:
            n += len(list(self._eflr_sets.get_all_items_for_set_type(eflr_set_type)))
        for mfd in multi_frame_data_objects:
            n += len(mfd)
        n += len(self._no_format_frame_data)

        def generator() -> Generator:
            if self.defining_origin is None:
                raise RuntimeError("No Origin defined for the file")

            yield self.file_header.parent
            yield from self._eflr_sets[eflr_types.OriginSet].values()

            for set_type, set_dict in self._eflr_sets.items():
                if set_type not in (eflr_types.FileHeaderSet, eflr_types.OriginSet):
                    yield from set_dict.values()

            yield from self._no_format_frame_data

            for multi_frame_data in multi_frame_data_objects:
                yield from multi_frame_data

        return SizedGenerator(generator(), size=n)

    def write(
            self,
            dlis_file_name: file_name_type,
            input_chunk_size: Optional[int] = None,
            output_chunk_size: Optional[number_type] = 2**32,
            data: Optional[data_form_type] = None,
            from_idx: int = 0,
            to_idx: Optional[int] = None
    ) -> None:
        """Create a DLIS file form the current specifications.

        Args:
            dlis_file_name          :   Name of the file to be created.
            input_chunk_size        :   Size of the chunks (in rows) in which input data will be loaded to be processed.
            output_chunk_size       :   Size of the buffers accumulating file bytes before file write action is called.
            data                    :   Data for channels - if not specified when channels were added.
            from_idx                :   Index from which the data should be loaded (or number of initial rows
                                        to ignore).
            to_idx                  :   Index up to which data should be loaded.
        """

        def timed_func() -> None:
            """Perform the action of creating a DLIS file.

            This function is used in a timeit call to time the file creation.
            """

            self.check_objects()

            logical_records = self.generate_logical_records(
                chunk_size=input_chunk_size, data=data, from_idx=from_idx, to_idx=to_idx)

            writer = DLISWriter(dlis_file_name, visible_record_length=self.storage_unit_label.max_record_length)
            writer.write_storage_unit_label(self.storage_unit_label)
            writer.write_logical_records(logical_records, output_chunk_size=output_chunk_size)

        exec_time = timeit(timed_func, number=1)
        logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")
