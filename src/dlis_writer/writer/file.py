import datetime
from typing import Any, Union, Optional, TypeVar
import numpy as np
import os
from timeit import timeit
from datetime import timedelta
import logging

from dlis_writer.utils.source_data_wrappers import DictDataWrapper, SourceDataWrapper
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.core.eflr import EFLRItem
from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.logical_record import eflr_types
from dlis_writer.logical_record.iflr_types.no_format_frame_data import NoFormatFrameData
from dlis_writer.logical_record.collections.file_logical_records import FileLogicalRecords
from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.writer.writer import DLISWriter


logger = logging.getLogger(__name__)


kwargs_type = dict[str, Any]
number_type = Union[int, float]
dtime_or_number_type = Union[datetime.datetime, int, float]
values_type = Optional[Union[list[str], list[int], list[float]]]


T = TypeVar('T')
ListOrTuple = Union[list[T], tuple[T, ...]]


class DLISFile:
    """Define the structure and contents of a DLIS and create a file based on the provided information."""

    def __init__(
            self,
            storage_unit_label: Optional[Union[StorageUnitLabel, kwargs_type]] = None,
            file_header: Optional[Union[eflr_types.FileHeaderItem, kwargs_type]] = None,
            origin: Optional[Union[eflr_types.OriginItem, kwargs_type]] = None
    ):
        """Initialise DLISFile.

        Args:
            storage_unit_label  :   An instance of StorageUnitLabel or keyword arguments to create one.
            file_header         :   An instance of FileHeaderObject or keyword arguments to create one.
            origin              :   An instance of OriginObject or keyword arguments to create one.
        """

        if isinstance(storage_unit_label, StorageUnitLabel):
            self._sul = storage_unit_label
        else:
            storage_unit_label = storage_unit_label or {}
            sid = storage_unit_label.get('set_identifier', 'MAIN STORAGE UNIT')
            self._sul = StorageUnitLabel(sid, **storage_unit_label)

        if isinstance(file_header, eflr_types.FileHeaderItem):
            self._file_header = file_header
        else:
            file_header = file_header or {}
            fid = file_header.get('identifier', 'FILE HEADER')
            self._file_header = eflr_types.FileHeaderItem(fid, **file_header)

        if isinstance(origin, eflr_types.OriginItem):
            self._origin = origin
        else:
            origin = origin or {}
            on = origin.get('name', 'ORIGIN')
            fsn = origin.get('file_set_number', 1)
            self._origin = eflr_types.OriginItem(on, file_set_number=fsn, **origin)

        self._channels: list[eflr_types.ChannelItem] = []
        self._frames: list[eflr_types.FrameItem] = []
        self._other_eflr: list[EFLRItem] = []
        self._no_format_frame_data: list[NoFormatFrameData] = []

        self._data_dict: dict[str, np.ndarray] = {}

    @property
    def storage_unit_label(self) -> StorageUnitLabel:
        """Storage Unit Label of the DLIS."""

        return self._sul

    @property
    def file_header(self) -> eflr_types.FileHeaderItem:
        """File header of the DLIS."""

        return self._file_header

    @property
    def origin(self) -> eflr_types.OriginItem:
        """Origin of the DLIS. Note: currently only adding a single origin is supported."""

        return self._origin

    @property
    def channels(self) -> list[eflr_types.ChannelItem]:
        """Channels defined for the DLIS."""

        return self._channels

    @property
    def frames(self) -> list[eflr_types.FrameItem]:
        """Frames defined for the DLIS."""

        return self._frames

    def add_axis(
            self,
            name: str,
            axis_id: Optional[str] = None,
            coordinates: values_type = None,
            spacing: Optional[number_type] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.AxisItem:
        """Define an axis (AxisObject) and add it to the DLIS.

        Args:
            name        :   Name of the axis.
            axis_id     :   ID of the axis.
            coordinates :   List of coordinates of the axis.
            spacing     :   Spacing of the axis.
            set_name    :   Name of the AxisSet this axis should be added to.
        """

        ax = eflr_types.AxisItem(
            name=name,
            axis_id=axis_id,
            coordinates=coordinates,
            spacing=spacing,
            set_name=set_name
        )

        self._other_eflr.append(ax)
        return ax

    def add_calibration(
            self,
            name: str,
            calibrated_channels: Optional[ListOrTuple[eflr_types.ChannelItem]] = None,
            uncalibrated_channels: Optional[ListOrTuple[eflr_types.ChannelItem]] = None,
            coefficients: Optional[ListOrTuple[eflr_types.CalibrationCoefficientItem]] = None,
            measurements: Optional[ListOrTuple[eflr_types.CalibrationMeasurementItem]] = None,
            parameters: Optional[ListOrTuple[eflr_types.ParameterItem]] = None,
            method: Optional[str] = None,
            set_name: Optional[str] = None
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
            set_name=set_name
        )

        self._other_eflr.append(c)
        return c

    def add_calibration_coefficient(
            self,
            name: str,
            label: Optional[str] = None,
            coefficients: Optional[list[number_type]] = None,
            references: Optional[list[number_type]] = None,
            plus_tolerances: Optional[list[number_type]] = None,
            minus_tolerances: Optional[list[number_type]] = None,
            set_name: Optional[str] = None,
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
            set_name=set_name
        )

        self._other_eflr.append(c)
        return c

    def add_calibration_measurement(
            self,
            name: str,
            phase: Optional[str] = None,
            measurement_source: Optional[eflr_types.ChannelItem] = None,
            measurement_type: Optional[str] = None,
            dimension: Optional[list[int]] = None,
            axis: Optional[eflr_types.AxisItem] = None,
            measurement: Optional[list[number_type]] = None,
            sample_count: Optional[int] = None,
            maximum_deviation: Optional[list[number_type]] = None,
            standard_deviation: Optional[list[number_type]] = None,
            begin_time: Optional[dtime_or_number_type] = None,
            duration: Optional[number_type] = None,
            reference: Optional[list[number_type]] = None,
            standard: Optional[list[number_type]] = None,
            plus_tolerance: Optional[list[number_type]] = None,
            minus_tolerance: Optional[list[number_type]] = None,
            set_name: Optional[str] = None
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
            set_name=set_name
        )

        self._other_eflr.append(m)
        return m

    def add_channel(
            self,
            name: str,
            data: Optional[np.ndarray] = None,
            dataset_name: Optional[str] = None,
            long_name: Optional[str] = None,
            representation_code: Optional[Union[str, int, RepresentationCode]] = None,
            dimension: Optional[Union[int, list[int]]] = None,
            element_limit: Optional[Union[int, list[int]]] = None,
            properties: Optional[list[str]] = None,
            units: Optional[str] = None,
            axis: Optional[eflr_types.AxisItem] = None,
            minimum_value: Optional[float] = None,
            maximum_value: Optional[float] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.ChannelItem:
        """Define a channel (ChannelItem) and add it to the DLIS.

        Args:
            name                :   Name of the channel.
            data                :   Data associated with the channel.
            dataset_name        :   Name of the data array associated with the channel in the data source provided
                                    at init of DLISFile.
            long_name           :   Description of the channel.
            properties          :   List of properties of the channel.
            representation_code :   Representation code for the channel data. Determined automatically if not provided.
            dimension           :   Dimension of the channel data. Determined automatically if not provided.
            element_limit       :   Element limit of the channel data. Determined automatically if not provided.
                                    Should be the same as dimension (in the current implementation of dlis_writer).
            units               :   Unit of the channel data.
            axis                :   Axis associated with the channel.
            minimum_value       :   Minimum value of the channel data.
            maximum_value       :   Maximum value of the channel data.
            set_name            :   Name of the ChannelSet this channel should be added to.

        Returns:
            A configured ChannelObject instance, which is already added to the DLIS (but not to any frame).
        """

        if data is not None and not isinstance(data, np.ndarray):
            raise ValueError(f"Expected a numpy.ndarray, got a {type(data)}: {data}")

        ch = eflr_types.ChannelItem(
            name,
            long_name=long_name,
            dataset_name=dataset_name,
            properties=properties,
            representation_code=representation_code,
            dimension=dimension,
            element_limit=element_limit,
            units=units,
            axis=axis,
            minimum_value=minimum_value,
            maximum_value=maximum_value,
            set_name=set_name
        )
        # skipping dimension and element limit because they will be determined from the data

        self._channels.append(ch)

        if data is not None:
            self._data_dict[ch.dataset_name] = data

        return ch

    def add_comment(
            self, name: str,
            text: Optional[list[str]] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.CommentItem:
        """Create a comment item and add it to the DLIS.

        Args:
            name        :   Name of the comment.
            text        :   Content of the comment.
            set_name    :   Name of the CommentSet this comment should be added to.

        Returns:
            A configured comment item.
        """

        c = eflr_types.CommentItem(
            name=name,
            text=text,
            set_name=set_name
        )

        self._other_eflr.append(c)
        return c

    def add_computation(
            self,
            name: str,
            long_name: Optional[str] = None,
            properties: Optional[list[str]] = None,
            dimension: Optional[list[int]] = None,
            axis: Optional[eflr_types.AxisItem] = None,
            zones: Optional[ListOrTuple[eflr_types.ZoneItem]] = None,
            values: Optional[list[number_type]] = None,
            source: Optional[EFLRItem] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.ComputationItem:
        """Create a computation item and add it to the DLIS.

        Args:
            name        :   Name of the computation.
            long_name   :   Description of the computation.
            properties  :   Properties of the computation.
            dimension   :   Dimension of the computation.
            axis        :   Axis associated with the computation.
            zones       :   Zones associated with the computation.
            values      :   Values of the computation.
            source      :   Source of the computation.
            set_name    :   Name of the ComputationSet this computation should be added to.

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
            set_name=set_name
        )

        self._other_eflr.append(c)
        return c

    def add_equipment(
            self,
            name: str,
            trademark_name: Optional[str] = None,
            status: Optional[int] = None,
            eq_type: Optional[str] = None,
            serial_number: Optional[str] = None,
            location: Optional[str] = None,
            height: Optional[number_type] = None,
            length: Optional[number_type] = None,
            minimum_diameter: Optional[number_type] = None,
            maximum_diameter: Optional[number_type] = None,
            volume: Optional[number_type] = None,
            weight: Optional[number_type] = None,
            hole_size: Optional[number_type] = None,
            pressure: Optional[number_type] = None,
            temperature: Optional[number_type] = None,
            vertical_depth: Optional[number_type] = None,
            radial_drift: Optional[number_type] = None,
            angular_drift: Optional[number_type] = None,
            set_name: Optional[str] = None
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
            set_name=set_name
        )

        self._other_eflr.append(eq)
        return eq

    def add_frame(
            self,
            name: str,
            channels: Optional[ListOrTuple[eflr_types.ChannelItem]],
            description: Optional[str] = None,
            index_type: Optional[str] = None,
            direction: Optional[str] = None,
            spacing: Optional[number_type] = None,
            encrypted: Optional[int] = None,
            index_min: Optional[number_type] = None,
            index_max: Optional[number_type] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.FrameItem:
        """Define a frame (FrameObject) and add it to the DLIS.

        Args:
            name        :   Name of the frame.
            channels    :   Channels associated with the frame.
            description :   Description of the frame.
            index_type  :   Description of the type of data defining the frame index.
            direction   :   Indication of whether the index has increasing or decreasing values. Allowed values:
                            'INCREASING', 'DECREASING'.
            spacing     :   Spacing between consecutive values in the frame index.
            encrypted   :   Indication whether the frame is encrypted (0 if not, 1 if yes).
            index_min   :   Minimum value of the frame index.
            index_max   :   Maximum value of the frame index.
            set_name    :   Name of the FrameSet this frame should be added to.

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
            set_name=set_name
        )

        self._frames.append(fr)
        return fr

    def add_group(
            self,
            name: str,
            description: Optional[str] = None,
            object_type: Optional[str] = None,
            object_list: Optional[ListOrTuple[EFLRItem]] = None,
            group_list: Optional[ListOrTuple[eflr_types.GroupItem]] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.GroupItem:
        """Create a group of EFLR items and add it to the DLIS.

        Args:
            name        :   Name of the group.
            description :   Description of the group.
            object_type :   Type of the objects contained in the group, e.g. CHANNEL, FRAME, PATH, etc.
            object_list :   List of the EFLR items to be added to this group.
            group_list  :   List of group items to be added to this group.
            set_name    :   Name of the FrameSet this frame should be added to.

        Returns:
            A configured group item.
        """

        g = eflr_types.GroupItem(
            name=name,
            description=description,
            object_type=object_type,
            object_list=object_list,
            group_list=group_list,
            set_name=set_name
        )

        self._other_eflr.append(g)
        return g

    def add_long_name(
            self,
            name: str,
            general_modifier: Optional[list[str]] = None,
            quantity: Optional[str] = None,
            quantity_modifier: Optional[list[str]] = None,
            altered_form: Optional[str] = None,
            entity: Optional[str] = None,
            entity_modifier: Optional[list[str]] = None,
            entity_number: Optional[str] = None,
            entity_part: Optional[str] = None,
            entity_part_number: Optional[str] = None,
            generic_source: Optional[str] = None,
            source_part: Optional[list[str]] = None,
            source_part_number: Optional[list[str]] = None,
            conditions: Optional[list[str]] = None,
            standard_symbol: Optional[str] = None,
            private_symbol: Optional[str] = None,
            set_name: Optional[str] = None
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
            set_name=set_name
        )

        self._other_eflr.append(ln)
        return ln

    def add_message(
            self,
            name: str,
            message_type: Optional[str] = None,
            time: Optional[dtime_or_number_type] = None,
            borehole_drift: Optional[number_type] = None,
            vertical_depth: Optional[number_type] = None,
            radial_drift: Optional[number_type] = None,
            angular_drift: Optional[number_type] = None,
            text: Optional[list[str]] = None,
            set_name: Optional[str] = None,
    ) -> eflr_types.MessageItem:
        """Create a message and add it to DLIS.

        Args:
            name            :   Name of the message.
            message_type    :   Type of the message.
            time            :   Time of the message.
            borehole_drift  :   Borehole drift.
            vertical_depth  :   Vertical depth.
            radial_drift    :   Radial drift.
            angular_drift   :   Angular drift.
            text            :   Text of the message.
            set_name        :   Name of the MessageSet this message should be added to.

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
            set_name=set_name
        )

        self._other_eflr.append(m)
        return m

    def add_no_format(
            self,
            name: str,
            consumer_name: Optional[str] = None,
            description: Optional[str] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.NoFormatItem:
        """Create a no-format item and add it to the DLIS.

        Args:
            name            :   Name of the no-format item.
            consumer_name   :   Consumer name.
            description     :   Description.
            set_name        :   Name of the NoFormatSet this item should be added to.

        Returns:
            A configured no-format item.
        """

        nf = eflr_types.NoFormatItem(
            name=name,
            consumer_name=consumer_name,
            description=description,
            set_name=set_name
        )

        self._other_eflr.append(nf)
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

        d = NoFormatFrameData()
        d.no_format_object = no_format_object
        d.data = data

        self._no_format_frame_data.append(d)
        return d

    def add_parameter(
            self,
            name: str,
            long_name: Optional[str] = None,
            dimension: Optional[list[int]] = None,
            axis: Optional[eflr_types.AxisItem] = None,
            zones: Optional[ListOrTuple[eflr_types.ZoneItem]] = None,
            values: values_type = None,
            set_name: Optional[str] = None
    ) -> eflr_types.ParameterItem:
        """Create a parameter.

        Args:
            name        :   Name of the parameter.
            long_name   :   Description of the parameter.
            dimension   :   Dimension of the parameter.
            axis        :   Axis associated with the parameter.
            zones       :   Zones the parameter is defined for.
            values      :   Values of the parameter - numerical or textual.
            set_name    :   Name of the ParameterSet this parameter should be added to.

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
            set_name=set_name
        )

        self._other_eflr.append(p)
        return p

    def add_path(
            self,
            name: str,
            frame_type: Optional[eflr_types.FrameItem] = None,
            well_reference_point: Optional[eflr_types.WellReferencePointItem] = None,
            value: Optional[ListOrTuple[eflr_types.ChannelItem]] = None,
            borehole_depth: Optional[number_type] = None,
            vertical_depth: Optional[number_type] = None,
            radial_drift: Optional[number_type] = None,
            angular_drift: Optional[number_type] = None,
            time: Optional[number_type] = None,
            depth_offset: Optional[number_type] = None,
            measure_point_offset: Optional[number_type] = None,
            tool_zero_offset: Optional[number_type] = None,
            set_name: Optional[str] = None
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
            set_name=set_name
        )

        self._other_eflr.append(p)
        return p

    def add_process(
            self,
            name: str,
            description: Optional[str] = None,
            trademark_name: Optional[str] = None,
            version: Optional[str] = None,
            properties: Optional[list[str]] = None,
            status: Optional[str] = None,
            input_channels: Optional[ListOrTuple[eflr_types.ChannelItem]] = None,
            output_channels: Optional[ListOrTuple[eflr_types.ChannelItem]] = None,
            input_computations: Optional[ListOrTuple[eflr_types.ComputationItem]] = None,
            output_computations: Optional[ListOrTuple[eflr_types.ComputationItem]] = None,
            parameters: Optional[ListOrTuple[eflr_types.ParameterItem]] = None,
            comments: Optional[list[str]] = None,
            set_name: Optional[str] = None
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
            set_name=set_name
        )

        self._other_eflr.append(p)
        return p

    def add_splice(
            self,
            name: str,
            output_channel: Optional[eflr_types.ChannelItem] = None,
            input_channels: Optional[ListOrTuple[eflr_types.ChannelItem]] = None,
            zones: Optional[ListOrTuple[eflr_types.ZoneItem]] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.SpliceItem:
        """Create a splice object.

        Args:
            name            :   Name of the splice.
            output_channel  :   Output of the splice.
            input_channels  :   Input of the splice.
            zones           :   Zones the splice is defined for.
            set_name        :   Name of the SpliceSet this splice should be added to.

        Returns:
            A configured splice.
        """

        sp = eflr_types.SpliceItem(
            name=name,
            output_channel=output_channel,
            input_channels=input_channels,
            zones=zones,
            set_name=set_name
        )
        self._other_eflr.append(sp)
        return sp

    def add_tool(
            self,
            name: str,
            description: Optional[str] = None,
            trademark_name: Optional[str] = None,
            generic_name: Optional[str] = None,
            parts: Optional[ListOrTuple[eflr_types.EquipmentItem]] = None,
            status: Optional[int] = None,
            channels: Optional[ListOrTuple[eflr_types.ChannelItem]] = None,
            parameters: Optional[ListOrTuple[eflr_types.ParameterItem]] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.ToolItem:
        """Create a tool object.

        Args:
            name            :   Name of the tool.
            description     :   Description of the tool.
            trademark_name  :   Trademark name.
            generic_name    :   Generic name.
            parts           :   Equipment this tool consists of.
            status          :   Status of the tool: 1 or 0.
            channels        :   Channels associated with this tool.
            parameters      :   Parameters associated with this tool.
            set_name        :   Name of the ToolSet this tool should be added to.

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
            set_name=set_name
        )

        self._other_eflr.append(t)
        return t

    def add_well_reference_point(
            self,
            name: str,
            permanent_datum: Optional[str] = None,
            vertical_zero: Optional[str] = None,
            permanent_datum_elevation: Optional[number_type] = None,
            above_permanent_datum: Optional[number_type] = None,
            magnetic_declination: Optional[number_type] = None,
            coordinate_1_name: Optional[str] = None,
            coordinate_1_value: Optional[number_type] = None,
            coordinate_2_name: Optional[str] = None,
            coordinate_2_value: Optional[number_type] = None,
            coordinate_3_name: Optional[str] = None,
            coordinate_3_value: Optional[number_type] = None,
            set_name: Optional[str] = None
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
            set_name=set_name
        )

        self._other_eflr.append(w)
        return w

    def add_zone(
            self,
            name: str,
            description: Optional[str] = None,
            domain: Optional[str] = None,
            maximum: Optional[dtime_or_number_type] = None,
            minimum: Optional[dtime_or_number_type] = None,
            set_name: Optional[str] = None
    ) -> eflr_types.ZoneItem:
        """Create a zone (ZoneObject) and add it to the DLIS.

        Args:
            name        :   Name of the zone.
            description :   Description of the zone.
            domain      :   Domain of the zone. One of: 'BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH'.
            maximum     :   Maximum of the zone.
            minimum     :   Minimum of the zone.
            set_name    :   Name of the ZoneSet this zone should be added to.

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
            set_name=set_name
        )

        self._other_eflr.append(z)
        return z

    def _make_multi_frame_data(self, fr: eflr_types.FrameItem, data: Union[dict, os.PathLike[str], np.ndarray] = None,
                               **kwargs) -> MultiFrameData:
        """Create a MultiFrameData object, containing the frame and associated data, generating FrameData instances."""

        if isinstance(data, dict):
            self._data_dict = self._data_dict | data
            data_object = DictDataWrapper(self._data_dict, mapping=fr.channel_name_mapping)
        else:
            if self._data_dict:
                raise TypeError(f"Expected a dictionary of np.ndarrays; got {type(data)}: {data} "
                                f"(Note: a dictionary is the only allowed type because some channels have been added"
                                f"with associated data arrays")
            data_object = SourceDataWrapper.make_wrapper(data, mapping=fr.channel_name_mapping)

        fr.setup_from_data(data_object)
        return MultiFrameData(fr, data_object, **kwargs)

    def make_file_logical_records(
            self,
            chunk_size: Optional[int] = None,
            data: Union[dict, os.PathLike[str], np.ndarray] = None
    ) -> FileLogicalRecords:
        """Create an iterable object of logical records to become part of the created DLIS file."""

        flr = FileLogicalRecords(
            sul=self._sul,
            fh=self._file_header.parent,
            orig=self._origin.parent
        )

        def get_parents(objects):
            return set(obj.parent for obj in objects)

        flr.add_channels(*get_parents(self._channels))
        flr.add_frames(*get_parents(self._frames))
        flr.add_frame_data_objects(
            *(self._make_multi_frame_data(fr, chunk_size=chunk_size, data=data) for fr in self._frames))
        flr.add_logical_records(*get_parents(self._other_eflr))
        flr.add_logical_records(*self._no_format_frame_data)

        return flr

    def write(self, dlis_file_name: Union[str, os.PathLike[str]], visible_record_length: int = 8192,
              input_chunk_size: Optional[int] = None, output_chunk_size: Optional[number_type] = 2**32,
              data: Union[dict, os.PathLike[str], np.ndarray] = None):
        """Create a DLIS file form the current specifications.

        Args:
            dlis_file_name          :   Name of the file to be created.
            visible_record_length   :   Maximal length of visible records to be created in the file.
            input_chunk_size        :   Size of the chunks (in rows) in which input data will be loaded to be processed.
            output_chunk_size       :   Size of the buffers accumulating file bytes before file write action is called.
            data                    :   Data for channels - if not specified when channels were added.
        """

        def timed_func():
            """Perform the action of creating a DLIS file.

            This function is used in a timeit call to time the file creation.
            """

            dlis_file = DLISWriter(visible_record_length=visible_record_length)
            logical_records = self.make_file_logical_records(chunk_size=input_chunk_size, data=data)
            dlis_file.create_dlis(logical_records, filename=dlis_file_name, output_chunk_size=output_chunk_size)

        exec_time = timeit(timed_func, number=1)
        logger.info(f"DLIS file created in {timedelta(seconds=exec_time)} ({exec_time} seconds)")


if __name__ == '__main__':
    # basic example for creating a DLIS file
    # for a more advanced example, see dlis-writer/examples/create_synth_dlis.py

    df = DLISFile()

    n_rows = 100
    ch1 = df.add_channel('DEPTH', data=np.arange(n_rows) / 10, units='m')
    ch2 = df.add_channel("RPM", data=(np.arange(n_rows) % 10).astype(float))
    ch3 = df.add_channel("AMPLITUDE", data=np.random.rand(n_rows, 5))
    main_frame = df.add_frame("MAIN FRAME", channels=(ch1, ch2, ch3), index_type='BOREHOLE-DEPTH')

    df.write('./tmp.DLIS', input_chunk_size=20)
