"""Define DLISFile: the interface to building a DLIS file structure.

Note: unless otherwise specified, all quotes come from teh RP66 v1 standard specification.
"""

from typing import Any, Union, Optional, TypeVar, Generator
import numpy as np
from timeit import timeit
from datetime import timedelta, datetime
import logging

from dlis_writer.utils.source_data_wrappers import DictDataWrapper, SourceDataWrapper
from dlis_writer.utils.types import (numpy_dtype_type, number_type, dtime_or_number_type, list_of_values_type,
                                     file_name_type, data_form_type, ListOrTuple, NestedList, AttrDict)
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
            fh_id: str = "FILE HEADER",
            fh_identifier: str = "0",
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
            fh_id               :   Used to create a FileHeaderItem.
                                    '[A] descriptive identification of the Logical File', max 65 characters long.
            fh_identifier       :   Used to create a FileHeaderItem.
                                    '[A] single arbitrary character', identifying the File Header.
            fh_sequence_number  :   Used to create a FileHeaderItem.
                                    'The ASCII representation of a positive integer that indicates
                                    the sequential position of the Logical File in a Storage Set'.
                                    A positive integer of max 10 digits.
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
            header_id=fh_id,
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
        """Define an axis (AxisItem) and add it to the DLIS.

        'An Axis Logical Record is an Explicitly Formatted Logical Record that contains information
        describing the coordinate axes of arrays.'

        Args:
            name                :   Name of the object.
            axis_id             :   '[An] (...) identifier for the coordinate axis described by this Object.'
            coordinates         :   '[E]xplicit coordinate values along a coordinate axis. These values may be numeric
                                    (i.e., for non-uniform coordinate spacing), or they may be textual identifiers,
                                    for example "Near" and "Far". If the Coordinates Value has numeric Elements,
                                    then they must occur in order of increasing or decreasing value.
                                    The Count of the Coordinates Attribute need not agree with the number
                                    of array elements along this axis specified by a related Dimension Attribute.'
            spacing             :   'The Spacing Attribute specifies a constant, signed spacing along the axis between
                                    successive coordinates, beginning at the last coordinate value specified
                                    by the Coordinates Attribute. If the Coordinates Attribute is non-numeric or absent,
                                    then the specified spacing is assumed to exist between every pair
                                    of successive coordinate values along the axis, and the first coordinate value
                                    is assumed to be zero (0).'
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

        'Calibration Objects identify the collection of measurements and coefficients that participate
        in the calibration of a Channel.'

        Args:
            name                    :   Name of the object.
            calibrated_channels     :   '[A] List of references to Channel Objects. The corresponding Channels
                                        (typically just one) are declared to be calibrated using the coefficients
                                        and measurements identified by the Coefficients and Measurements Attributes
                                        described below.'
            uncalibrated_channels   :   '[A] List of references to Channel Objects. The corresponding Channels
                                        (typically just one) are used, along with coefficients and according
                                        to the computational method, to compute the Channels identified
                                        by the Calibrated-Channels Attribute.'
            coefficients            :   '[A] List of references to Calibration-Coefficient Objects. The coefficients,
                                        references, and tolerances collectively defined by these Objects are used
                                        to compute the Channels identified by the Calibrated-Channels Attribute.'
            measurements            :   '[A] List of references to Calibration-Measurement Objects. The measurements
                                        collectively defined by these Objects are used to derive the coefficients
                                        that are used to calibrate the Channels identified by the Calibrated-Channels
                                        Attribute.'
            parameters              :   '[A] List of references to Parameter Objects. The referenced Objects provide
                                        information directly associated with the calibration process, for example
                                        statistics, quality control indicators, parameters entered by the operator,
                                        vendor-supplied coefficients, and other information (numeric or textual)
                                        that is potentially of interest to the Consumer.'
            method                  :   '[D]efines the computational method used to calibrate the Channels identified
                                        by the Calibrated-Channels Attribute. (...) For the simple model described
                                        earlier [gain and offset calibration], the Method might be "Two-Point-Linear".'
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

        'Calibration-Coefficient Objects record coefficients, their references, and tolerances
        used in the calibration of Channels.'

        Args:
            name                :   Name of the object.
            label               :   '[A] label for the coefficients that identifying their role in the calibration
                                    process. Values of this Attribute are dictionary-controlled terms. For the simple
                                    model described earlier [gain and offset calibration], the Label is "Gain"
                                    or "Offset".'
            coefficients        :   '[C]oefficients corresponding to the label in the Label Attribute.'
            references          :   '[R]eferences corresponding to the coefficients in the CoefficientS Attribute.
                                    Each recorded reference represents in some sense the nominal value
                                    of the corresponding recorded coefficient.'
            plus_tolerances     :   '[V]alues that indicate by how much a coefficient may exceed a reference
                                    and still be "within tolerance". Elements of this Attribute are all
                                    non-negative numbers. The convention that a coefficient be within tolerance
                                    is that it be less than or equal to the sum of the corresponding reference
                                    and plus tolerance.
                                    The recorded plus tolerance represents in some sense the maximum acceptable range
                                    of the recorded coefficient above the value of the recorded reference.
                                    If the Plus-Tolerances Attribute is absent, then plus tolerance
                                    is implicitly infinite.
                                    For the simple case [of nominal gain = 1 and nominal offset = 0], a Gain of 1.05
                                    is within tolerance when its reference is 1.0 and its plus tolerance is 0.1.
                                    It is out of tolerance when its reference is 1.0 and its plus tolerance is 0.01.'
            minus_tolerances    :   '[V]alues that indicate by how much a coefficient may fall short of a reference
                                    and still be "within tolerance". Elements of this Attribute are all
                                    non-negative numbers. The convention that a coefficient be within tolerance
                                    is that it be greater than or equal to the difference of the corresponding reference
                                     and minus tolerance.
                                    The recorded minus tolerance represents in some sense the maximum acceptable range
                                    of the recorded coefficient below the value of the recorded reference.
                                    If the Minus-Tolerances Attribute is absent, then minus tolerance
                                    is implicitly infinite.
                                    For the simple case illustrated earlier, a Gain of .95 is within tolerance
                                    when its reference is 1.0 and its minus tolerance is 0.1.
                                    It is out of tolerance when its reference is 1.0 and its minus tolerance is 0.01.'
            set_name            :   Name of the CorrelationCoefficientSet this item should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Notes:
            Attributes 'coefficients', 'references', 'plus_tolerances', and 'minus_tolerances' must have the same number
            of values.

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
            measurement_source: OptAttrSetupType[EFLRItem] = None,
            measurement_type: OptAttrSetupType[str] = None,
            dimension: OptAttrSetupType[list[int]] = None,
            axis: OptAttrSetupType[eflr_types.AxisItem] = None,
            measurement: OptAttrSetupType[NestedList[number_type]] = None,
            sample_count: OptAttrSetupType[int] = None,
            maximum_deviation: OptAttrSetupType[NestedList[number_type]] = None,
            standard_deviation: OptAttrSetupType[NestedList[number_type]] = None,
            begin_time: OptAttrSetupType[dtime_or_number_type] = None,
            duration: OptAttrSetupType[number_type] = None,
            reference: OptAttrSetupType[NestedList[number_type]] = None,
            standard: OptAttrSetupType[NestedList[number_type]] = None,
            plus_tolerance: OptAttrSetupType[NestedList[number_type]] = None,
            minus_tolerance: OptAttrSetupType[NestedList[number_type]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.CalibrationMeasurementItem:
        """Define a calibration measurement item and add it to the DLIS.

        'Calibration-Measurement Objects record measurements, references, and tolerances used to compute
        calibration coefficients'

        Args:
            name                :   Name of the object.
            phase               :   '[A] (...) code indicating what phase in the overall job sequence is represented
                                    by the current measurement.'
                                    Allowed values:
                                        - 'AFTER': 'After survey calibration',
                                        - 'BEFORE': 'Before survey calibration',
                                        - 'MASTER': 'Master calibration'.
            measurement_source  :   '[R]eferences an Object that specifies the source of the data recorded in
                                    the Measurement Attribute.' This can be e.g. a Channel object.
            measurement_type    :   '[T]he type of measurement taken. (...) For the simple model described earlier
                                    [measurement of gain and offset], the Type is "Zero" [for gain] or "Plus"
                                    [for offset].'
            dimension           :   '[S]pecifies the array structure of samples recorded in the Measurement Attribute,
                                    of the Reference Attribute, of the Maximum-Deviation Attribute,
                                    of the Standard-Deviation Attribute, of the Standard Attribute,
                                    of the Plus-Tolerance Attribute, and of the Minus-Tolerance Attribute (...).'
            axis                :   Axis of the measurement.
            measurement         :   '[A] measurement, possibly containing many samples, related to the uncalibrated data
                                    and described by the Type Attribute. The measurement may represent values of,
                                    an average of, or some other function of the uncalibrated data.'
            sample_count        :   '[T]he number of samples used to compute the Maximum-Deviation
                                    and Standard-Deviation.'
            maximum_deviation   :   '[M]eaningful only when the Measurement Attribute contains a single sample.
                                    In this case, the measurement is considered to be a mean, and Maximum-Deviation
                                    represents the maximum deviation from this mean of any sample used to compute
                                    the mean. For array samples, the mean and maximum deviation are computed
                                    independently for each sample Element. The deviation for any Element from the mean
                                    is computed as an absolute value.'
            standard_deviation  :   '[M]eaningful only when the Measurement Attribute contains a single sample.
                                    In this case, the measurement is considered to be a mean, and Standard-Deviation
                                    represents the statistical standard deviation of the samples used to compute
                                    the mean. For array samples, the mean and standard deviation are computed
                                    independently for each sample Element.'
            begin_time          :   '[T]he time at which acquisition of the measurement in the Measurement Attribute
                                    began. The Value of this Attribute represents either an absolute date and time
                                    (...) or an elapsed time from the file creation time specified by the Creation-Time
                                    Attribute of the Origin Object.'
            duration            :   '[A] time interval representing the acquisition duration of the measurement
                                    in the Measurement Attribute.'
            reference           :   '[T]he expected nominal value of a single sample of the measurement represented
                                    in the Measurement Attribute.'
            standard            :   '[T]he measurable quantity of the calibration standard used to produce the Value
                                    of the Measurement Attribute. For example, a standard used to calibrate a caliper
                                    is a steel ring. Its measurable quantity is its inside diameter, say 8 inches.
                                    The Measurement and Reference Attributes may represent the same physical quantity
                                    as the calibration standard, e.g., length. In this case, the Standard provides
                                    the same information as the Reference and is normally absent to avoid redundancy.
                                    It is possible, however, for the Measurement and Reference Attributes to represent
                                    a different physical quantity, say voltage. In this case, the Standard Attribute
                                    is required to describe the transformation from the physical quantity represented
                                    by the Measurement and Reference Attributes to the physical quantity
                                    of the calibration standard, e.g., from millivolts to inches. Deriving this
                                    transformation may require the Values of the Standard Attributes from more than one
                                    Calibration-Measurement Object.'
            plus_tolerance      :   '[I]ndicates by how much each measurement sample may exceed a reference and still
                                    be "within tolerance". Elements of this Attribute are all non-negative numbers.
                                    If a measurement sample is an array, then so is its reference and plus tolerance.
                                    The convention that a measurement sample be within tolerance is that each element
                                    of the measurement sample array be less than or equal to the sum of the
                                    corresponding reference and plus tolerance array elements.
                                    The plus tolerance represents in some sense the maximum acceptable drift of each
                                    recorded measurement sample above the value of the recorded reference.
                                    If the Plus-Tolerance Attribute is absent, then the plus tolerance
                                    is implicitly infinite.
                                    For the common simple case when a measurement sample is scalar, the sample value 352
                                    is within tolerance when its reference is 350 and its plus tolerance is 5.
                                    It is out of tolerance when its reference is 300 and its plus tolerance is 50.'
            minus_tolerance     :   '[I]ndicates by how much each measurement sample may fall below a reference
                                    and still be "within tolerance". Elements of this Attribute are all
                                    non-negative numbers. If a measurement sample is an array, then so is its reference
                                    and minus tolerance. The convention that a measurement sample be within tolerance
                                    is that each element of the measurement sample array be greater than or equal
                                    to the difference of the corresponding reference and minus tolerance array elements.
                                    The minus tolerance represents in some sense the maximum acceptable drift of each
                                    recorded measurement sample below the value of the recorded reference.
                                    If the Minus-Tolerance Attribute is absent, then the minus tolerance
                                    is implicitly infinite.
                                    For the common simple case when a measurement sample is scalar, the sample value 348
                                    is within tolerance when its reference is 350 and its minus tolerance is 5.
                                    It is out of tolerance when its reference is 400 and its minus tolerance is 50.'
            set_name            :   Name of the CorrelationMeasurementSet this measurement should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured CalibrationMeasurementItem instance.
        """

        m = eflr_types.CalibrationMeasurementItem(
            name=name,
            phase=phase,
            measurement_source=measurement_source,
            type=measurement_type,
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
            long_name: OptAttrSetupType[Union[eflr_types.LongNameItem, str]] = None,
            dimension: OptAttrSetupType[Union[int, list[int]]] = None,
            element_limit: OptAttrSetupType[Union[int, list[int]]] = None,
            properties: OptAttrSetupType[list[str]] = None,
            units: OptAttrSetupType[str] = None,
            axis: OptAttrSetupType[eflr_types.AxisItem] = None,
            minimum_value: OptAttrSetupType[float] = None,
            maximum_value: OptAttrSetupType[float] = None,
            source: OptAttrSetupType[EFLRItem] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.ChannelItem:
        """Define a channel (ChannelItem) and add it to the DLIS.

        'Channel Objects (...) identify Channels and specify their properties and their representation in Frames.
        The actual Channel sample values are recorded in Indirectly Formatted Logical Records, when present.'

        Args:
            name                :   Name of the object.
            data                :   Data associated with the Channel.
            dataset_name        :   Name of the data array associated with the Channel in the data source provided
                                    at init of DLISFile.
            cast_dtype          :   Numpy data type the Channel data should be cast to - e.g. np.float64, np.int32.
            long_name           :   Description of the Channel.
            properties          :   '[A] List of Property Indicators (...). The Property Indicators summarize the
                                    characteristics of the Channel and the processing that has occurred to produce it.'
                                    See dlis_writer.utils.enums.PROPERTIES for allowed values.
            dimension           :   Dimension of the Channel data. Determined automatically if not provided.
                                    '[T]he array structure of a sample value for the Channel'
            element_limit       :   Element limit of the Channel data. Determined automatically if not provided.
                                    '[S]pecifies limits on the dimensionality and size of a Channel sample.
                                    The Count of this Attribute specifies the maximum allowable number of dimensions,
                                    and each Element of this Attribute specifies the maximum allowable size
                                    of the corresponding dimension in array elements.
                                    For example, if Element-Limit = {5 10 50}, then a Channel sample may have
                                    0, 1, 2, or 3 dimensions. The first dimension size may be no larger than 5 elements,
                                    the second no larger than 10 elements, and the last no larger than 50 elements.
                                    Within these limits, the Channel sample may be of arbitrary size
                                    as specified by the Dimension Attribute (...).'
            units               :   Unit of the Channel data.
            axis                :   Axis associated with the Channel.
            minimum_value       :   Minimum value of the Channel data.
            maximum_value       :   Maximum value of the Channel data.
            source              :   '[A] reference to another Object that describes the immediate source of the Channel,
                                    for example, a TOOL, PROCESS, SPLICE, or CALIBRATION Object.'
            set_name            :   Name of the ChannelSet this Channel should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured ChannelItem instance, which is already added to the DLIS (but not to any frame).
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
            source=source,
            parent=self._eflr_sets.get_or_make_set(eflr_types.ChannelSet, set_name=set_name),
            origin_reference=origin_reference or self.default_origin_reference
        )

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
            name                :   Name of the object.
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
            axis: OptAttrSetupType[ListOrTuple[eflr_types.AxisItem]] = None,
            zones: OptAttrSetupType[ListOrTuple[eflr_types.ZoneItem]] = None,
            values: OptAttrSetupType[NestedList[number_type]] = None,
            source: OptAttrSetupType[EFLRItem] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.ComputationItem:
        """Create a computation item and add it to the DLIS.

        'Computation Objects (...) contain results of computations that are more appropriately expressed as Static
        Information rather than as Channels. Computation Objects are similar to Parameter Objects, except that
        Computation Objects may be associated with Property Indicators, and Computation Objects may be the output
        of PROCESS Objects (...).'

        Args:
            name                :   Name of the object.
            long_name           :   Description of the computation.
            properties          :   '[A] List of Property Indicators (...). The Property Indicators summarize
                                    the characteristics of the Computation and the processing that has occurred
                                    to produce it.'
                                    See dlis_writer.utils.enums.PROPERTIES for allowed values.
            dimension           :   '[S]pecifies the array structure of a single value of the current Computation'
            axis                :   An Axis Object (AxisItem) associated with the computation.
            zones               :   '[A] List of Zone Objects that specify mutually disjoint intervals over which
                                    the value of the current Computation is constant. A Computation may have different
                                    values in different zones. When this Attribute is present, the Computation is said
                                    to be Zoned, and it is considered to be defined only in the zones specified
                                    by the Zones Attribute. It is considered to be undefined elsewhere.
                                    The Zone Objects referenced in this List must all have the same Domain Attribute
                                    Value. That is, a Computation Object may only be zoned over a single domain.
                                    The Zones Attribute may be absent, in which case the Computation is said to be
                                    Unzoned. In this case, the Computation is considered to be defined everywhere.'
            values              :   '[A] List of Computation values corresponding to the zones listed in the Zones
                                    Attribute. When the Computation is Zoned, the number of Computation values is
                                    the same as the number of zones referenced, and the k-th Computation value applies
                                    to the k-th zone. When the Computation is Unzoned, there is a single Computation
                                    value in the Values Attribute.'
            source              :   '[A] reference to another Object that describes the immediate source of the
                                    Computation, for example, a PROCESS Object.'
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
        """Define an equipment item.

        Equipment Objects (...) specify the presence and characteristics of surface and downhole equipment
        used in the acquisition of data. The purpose of this Object is to record information about individual pieces
        of equipment of any sort that is used during a job. The Tool Object (...) provides a way to collect equipment
        together in ensembles that are more readily recognizable to the Consumer.'

        Args:
            name                :   Name of the object.
            trademark_name      :   '[T]he name used by the Producer to refer to the Equipment.'
            status              :   '[I]ndicates the operational status of the equipment'. Integer, 1 or 0.
            eq_type             :   '[T]he generic type of the equipment'.
                                    See EquipmentItem.TYPE_OPTIONS for values allowed by RP66.
            serial_number       :   Serial number of the equipment.
            location            :   '[T]he general location of the equipment during acquisition.'
                                    See EquipmentItem.LOCATION_OPTIONS for values allowed by RP66.
            height              :   '[A]pplies only to equipment located in the borehole. It specifies the height of the
                                    bottom of the equipment above the Tool Zero Point when the tool string containing
                                    the equipment is vertical. This value is positive when the equipment bottom is above
                                    the Tool Zero Point and is negative when the equipment bottom is below the Tool
                                    Zero Point. There is normally one piece of equipment for which the height is zero.'
            length              :   '[S]pecifies the length of the equipment and is typically measured from bottom
                                    make up point to top make up point. It may not apply to surface equipment.
                                    The total length of the tool string may not equal the sum of the lengths
                                    of all the equipment that make up the tool string, since some equipment may slip
                                    over other equipment. Such "slip-on" equipment includes, for example, standoffs,
                                    centralizers, and excentralizers. Similarly, the height of a piece of equipment
                                    may be independent of the lengths of the equipment below it.'
            minimum_diameter    :   '[A]pplies to equipment used in the borehole. It specifies a minimum outer diameter
                                    of the equipment. This is defined to be the minimum horizontal cross-sectional
                                    diameter measured when the equipment is in a vertical configuration. For extendible
                                    or compressible equipment (e.g., caliper arms and centralizers), this measurement
                                    indicates the smallest operational diameter possible.'
            maximum_diameter    :   '[A]pplies to equipment used in the borehole. It specifies a maximum outer diameter
                                    of the equipment. This is defined to be the maximum horizontal cross-sectional
                                    diameter measured when the equipment is in a vertical configuration. For extendible
                                    or compressible equipment (e.g., caliper arms and centralizers), this measurement
                                    indicates the largest operational diameter possible.'
            volume              :   '[S]Specifies the volume of the equipment and is typically used to determine
                                    bouyant weight of the equipment. It may not apply to surface equipment.'
            weight              :   '[S]pecifies the weight of the equipment in air. It may not apply to surface
                                    equipment.'
            hole_size           :   '[A]pplies to equipment in the borehole. It specifies the minimum borehole diameter
                                    for which the equipment may reasonably be used.'
            pressure            :   '[I]ndicates the maximum operational pressure rating of the equipment,
                                    when applicable.'
            temperature         :   '[I]ndicates the maximum operational temperature rating of the equipment,
                                    when applicable.'
            vertical_depth      :   Vertical depth; see Notes below.
            radial_drift        :   Radial drift; see Notes below.
            angular_drift       :   Angular drift; see Notes below.
            set_name            :   Name of the EquipmentSet this equipment should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Notes:
            'The Vertical-Depth, Radial-Drift, and Angular-Drift Attributes specify the corresponding position
            coordinates, relative to the Well Reference Point (see §4.1.8), of the equipment represented
            by the current Object. These Attributes are intended to be used for surface equipment — for example,
            a geophone — that is stationary over a period of time.'

        Returns:
            A configured EquipmentItem instance.
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
        """Define a frame (FrameItem) and add it to the DLIS.

        'A Frame constitutes the Indirectly Formatted Data of a Type FDATA Indirectly Formatted Logical Record (IFLR).
        The Data Descriptor Reference of the FDATA Logical Record refers to a Frame Object (...)
        and defines the Frame Type of the Frame.
        Frames of a given Frame Type occur in sequences within a single Logical File.
        A Frame is segmented into a Frame Number, followed by a fixed number of Slots that contain Channel samples,
        one sample per Slot. The Frame Number is an integer (Representation Code UVARI) specifying the numerical order
        of the Frame in the Frame Type, counting sequentially from one. All Frames of a given Frame Type record the same
        Channels in the same order. The IFLRs containing Frames of a given Type need not be contiguous.

        A Frame Type may or may not have an Index Channel. If there is an Index Channel, then it must appear first
        in the Frame and it must be scalar. When an Index Channel is present, then all Channels in the Frame are assumed
        to be "sampled at" the Index value. For example, if the Index is depth, then Channels are sampled at the given
        depth; if time, then they are sampled at the given time, etc. (...)

        The truth of the assumption just stated is relative to the measuring and recording system used and does not
        imply absolute accuracy. For example, depth may be measured by a device that monitors cable movement
        at the surface, which may differ from actual tool movement in the borehole. Corrections that are applied
        to Channels to improve the accuracy of measurements or alignments to indices are left to the higher-level
        semantics of applications.

        When there is no Index Channel, then Frames are implicitly indexed by Frame Number.'

        Args:
            name                :   Name of the object.
            channels            :   Channels associated with the Frame.
                                    Note: a channel must not be referred to by more than one Frame.
                                    If two Frames are to contain the same data, then 'copies' of the relevant channels
                                    must be created.
            description         :   Description of the Frame.
            index_type          :   Description of the type of data defining the Frame's index.
                                    This is the data contained in the first Channel added to the Frame.
                                    Note: if index_type is not specified, then the Frame is assumed to have no index
                                    Channel. In this case, 'direction' and 'spacing' attributes of the Frame
                                    are ignored (according to the standard; they are still passed to the saved file).
            direction           :   Indication of whether the Frame index has increasing or decreasing values.
                                    Allowed values: 'INCREASING', 'DECREASING'.
            spacing             :   Spacing between consecutive values in the frame index.
                                    If 'direction' is 'DECREASING', then the spacing value should be negative.
                                    If 'spacing' is defined, 'direction' is not required.
                                    'Presence of this Attribute guarantees to the Consumer that Index spacing
                                    will be constant for the current Frame Type throughout the Logical File.
                                    If the Index spacing is allowed to change, then this Attribute must be absent.'
            encrypted           :   Indication whether the frame is encrypted (0 if not, 1 if yes).
                                    'Encrypted Frames typically contain information considered proprietary
                                    by the Producer.'
            index_min           :   Minimum value of the Frame index (the index Channel of the Frame).
                                    'If there is no Index Channel, then this is the minimum Frame Number, namely 1.'
            index_max           :   Maximum value of the Frame index (the index Channel of the Frame).
                                    'If there is no Index Channel, then this is the number of Frames in the Frame Type'
                                    (i.e. 'the number of rows' in the data table in which Channels are
                                    the (sets of) columns).
            set_name            :   Name of the FrameSet this frame should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Note:
            Values: direction, spacing, index_min, and index_max are automatically determined if not provided.
            However, in some cases it might be beneficial - and more accurate - to explicitly specify these values.

        Returns:
            A configured FrameItem instance, added to the DLIS.
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
            object_list: OptAttrSetupType[ListOrTuple[EFLRItem]] = None,
            group_list: OptAttrSetupType[ListOrTuple[eflr_types.GroupItem]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.GroupItem:
        """Create a group of EFLR items and add it to the DLIS.

        Args:
            name                :   Name of the object.
            description         :   Description of the group.
            object_list         :   '[A] List of references to arbitrary Objects (...). These Objects are considered
                                    to be related in some fashion known to the Producer.' The objects do not have to
                                    all be of the same type - e.g. a group containing a mix of Axis, Parameter, and
                                    Channel objects can be defined.
            group_list          :   '[A] List of references to other Group Objects. The Group Objects referenced
                                    are completely arbitrary.' The types of objects referenced by these groups might
                                    be different from other objects referenced by the current group.
            set_name            :   Name of the FrameSet this frame should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured group item.
        """

        g = eflr_types.GroupItem(
            name=name,
            description=description,
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
        """Create a Long Name item and add it to the DLIS.

        'Long-Name Objects represent structured names of other Objects.
        A Long–Name Object is referenced by (an Attribute of) the Object of which it is the structured name.
        There are standardized Name Part Types corresponding to the Labels of the Attributes of the Long-Name Object.
        For each Name Part Type there is a dictionary-controlled Lexicon of Name Part Values.
        A Name Part Value is a word or phrase. The Long Name is built by selecting those Name Part Types
        that are applicable to an Object and then selecting for each Name Part Type one or more Name Part Values
        from the corresponding Lexicons.'

        Args:
            name                :   Name of the object.
            general_modifier    :   '[Q]ualifies the Long Name otherwise specified by all the remaining Attributes
                                    of the Long-Name Object.'
            quantity            :   '[S]pecifies something that is measurable, for example physical dimensionality,
                                    or some classifiable feature of an entity, for example a name or color or shape'
            quantity_modifier   :   '[I]dentifies a specialization of a quantity; that is, it acts as an adjective
                                    applied to the Quantity Attribute Value.'
            altered_form        :   '[A] relationship to the Quantity Attribute Value. For example,
                                    "Standard Deviation" is an altered form of the quantity "Pressure".'
            entity              :   '[S]pecifies that thing of which the quantity is measured.
                                    For example, "Diameter" is a quantity of the entity "Borehole".'
            entity_modifier     :   '[I]dentifies a specialization of an entity; that is, it acts as an adjective
                                    applied to the Entity Attribute Value.'
            entity_number       :   '[D]istinguishes multiple instances of the same entity.'
            entity_part         :   '[I]dentifies a specific part of an entity.'
            entity_part_number  :   '[D]istinguishes multiple instances of the same entity part, for example,
                                    "Button 1", "Arm 2".'
            generic_source      :   '[S]pecifies briefly and generally the source of the information.
                                    The generic source of a borehole diameter measurement might be either
                                    "2-Arm Caliper" or "4–Arm Caliper".'
            source_part         :   '[I]dentifies a specific part of the source of the information specified
                                    by the Generic-Source Attribute, for example, "Receiver" or "Transmitter".'
            source_part_number  :   '[D]istinguishes multiple instances of the same source part.'
            conditions          :   '[C]onditions applicable at the time the information was acquired or generated.
                                    A condition of resistivity, for example, is "At Standard Temperature."'
            standard_symbol     :   '[A]n industry-standardized symbolic name by which the information is known.
                                    The possible values of this Attribute are specified by POSC. Consequently, this
                                    Attribute is optional and is used only when an applicable standardized name exists.'
            private_symbol      :   '[P]rovides an association between the recorded information and corresponding
                                    records or objects of the Producer’s internal or corporate database.
                                    The value used in this Attribute and the way in which the value is assigned
                                    are completely at the discretion of the Producer that is identified
                                    in the Origin Object associated with the Long Name Object.'
            set_name            :   Name of the LongNameSet this long name item should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured Long Name item.
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
            name                :   Name of the object.
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
        """Create a no-format (a subtype of unformatted data logical record) item and add it to the DLIS.

        'Unformatted Data Logical Records are Indirectly Formatted Logical Records of Type NOFORM that contain
        "packets" of unformatted (in the DLIS sense) binary data. The Data Descriptor reference of the NOFORM
        Logical Record refers to a NO-FORMAT Object (...). The purpose of Unformatted Data Logical Records is
        to transport arbitrary data that is of value to the Consumer, the format of which is known by the Consumer,
        but which has no DLIS Semantic meaning.

        NO-FORMAT Objects identify packet sequences of unformatted binary data. The Indirectly Formatted Data field
        of each NOFORM IFLR that references a given No-Format Object contains a segment of the source stream
        of unformatted data. This source stream is recovered by concatenating these segments in the same order
        in which they occur in the NOFORM IFLRs. Each segment of the source stream is considered under the DLIS
        to be a sequence of bytes, and no conversion is applied to the bytes as they are placed into the IFLRs
        nor as they are removed from the IFLRs.'

        Args:
            name                :   Name of the object.
            consumer_name       :   '[A] client-provided name for the data, for example an external file specification.'
            description         :   Description of the data item.
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

        A no-format frame data object forms a data item, multiple of which can be collected under a NoFormatItem
        descriptor (see add_no_format method).

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

        'ORIGIN Objects uniquely identify Logical Files and describe the basic circumstances under which Logical Files
        are created. ORIGIN Objects also provide a means for distinguishing different instances of a given entity.
        Each Logical File must contain at least one ORIGIN Set, which may contain one or more ORIGIN Objects.
        The first Object in the first ORIGIN Set is the Defining Origin for the Logical File in which it is contained,
        and the corresponding Logical File is called the Origin'’s Parent File.
        It is intended that no two Logical Files will ever have Defining Origins with all Attribute Values identical.'

        Args:
            name                :   Name of the object.
            file_set_number     :   File set number. Used as 'origin reference' in all other objects added to the file.
                                    If not specified, it is assigned randomly (in accordance with the RP66 specs).
                                    '[A] random number, called the File Set Number, that is used to distinguish
                                    the Logical Files of one File Set from the Logical Files of another File Set.
                                    This number should be such that there is a high probability that it uniquely
                                    identifies the File Set. This number should be the same for all Logical Files
                                    of a given File Set. This Attribute must be present, even when the File-Set-Name
                                    Attribute is absent. In that case, it is considered to apply to the File Set
                                    consisting of the single current Logical File.'
            file_set_name       :   '[T]he name of a File Set, a group of Logical Files related according to
                                    Producer-defined criteria to which the Parent File belongs.
                                    The File Set is an arbitrary grouping of a set of Logical Files
                                    and has no DLIS semantic meaning. The File-Set-Name Attribute is not expected
                                    to be unique for all File Sets.'
            file_id             :   '[A]n exact copy of the ID Attribute of the File-Header Object of the Parent File,
                                    i.e., the Logical File for which this Origin Object is the Defining Origin.'
                                    For defining origin (the first origin in the file) this will be set automatically,
                                    so it does not have to be specified here. For other origins - origins defining other
                                    DLIS files - the file_id should be specified manually.
            file_number         :   '[T]he File Number of the Parent File relative to the File Set specified by the
                                    File-Set-Name Attribute. File Numbers for a File Set are positive and increase
                                    in the order in which the Logical Files of the File Set are created.
                                    File Numbers for a File Set need not increase sequentially. It should be true,
                                    with a high probability, that no two Logical Files will ever have the same
                                    File Set Number and File Number combination. Notice that there is no specific
                                    relationship defined for File Numbers of Logical Files in the same Storage Set.
                                    In particular, a File Set may or may not coincide with the Logical Files
                                    of a Storage Set.'
            file_type           :   '[A] Producer-specified File Type and signifies the general contents of
                                    the Parent File or the circumstances under which the Parent File was created.'
            product             :   '[T]he name of the software product (e.g., the wellsite "operating" system)
                                    that produced the Parent File.'
            version             :   '[T]he version of the product specified by the Product Attribute.'
            programs            :   '[A] List of the names of a specific programs or services, operating as part
                                    of the software specified by the Product Attribute, that were used to generate
                                    the data contained in the Parent File.'
            creation_time       :   '[T]he date and time at which the Parent File was created.'
                                    If not specified, it is set to the current date and time.
            order_number        :   '[A] unique accounting number associated with the acquisition or creation
                                    of the data in the Parent File. It is typically known as the Service Order Number.'
            descent_number      :   '[M]eaningful to the Producer. The meaning of this number is specified
                                    by the Producer to the Consumer by means external to the DLIS.'
            run_number          :   '[M]eaningful to the company specified in the Company Attribute.
                                    Its use is specified to the Producer by this company by means external to the DLIS.'
            well_id             :   '[A] codified identifier of the well in or about which measurements were taken.
                                    Whenever applicable, the API Well Number should be used. This is a unique,
                                    permanent, numeric identifier assigned to a well in accordance with
                                    the American Petroleum Institute Bulletin D12A, January, 1979.'
            well_name           :   '[T]he name of the well.'
            field_name          :   '[T]he name of the Field to which the well belongs. If there is no Field,
                                    then the value of this Attribute should be WILDCAT.'
                                    That default is set automatically before writing the Origin if no value has been
                                    specified (i.e. the value is None).
            producer_code       :   '[T]he Producer’s identifying code. The Producer is the company whose authorized
                                    agent generated the Logical File using software programs developed under
                                    the sponsorship of the company. This code is assigned on request by POSC.
                                    A list of current Company Codes for Producers may be obtained from the same source.'
            producer_name       :   '[T]he Producer’s business or organization name'.
            company             :   '[T]he name of the client company for which the data was acquired or computed,
                                    typically the operator of the well.'
            name_space_name     :   '[S]pecifies the name of the dictionary in which dictionary-controlled Object Names
                                    are administered for this Origin. Each Producer is expected to administer
                                    or subscribe to a dictionary of Object Names from which meaningful definitions
                                    can be derived.'
            name_space_version  :   '[S]pecifies the version of the dictionary in which dictionary-controlled
                                    Object Names are administered for this Origin. Dictionary version N is a superset
                                    of dictionary version M whenever N > M.'
            set_name            :   Name of the OriginSet this origin should be added to.

        Returns:
            A configured OriginItem instance.
        """

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
            long_name: OptAttrSetupType[Union[str, eflr_types.LongNameItem]] = None,
            dimension: OptAttrSetupType[list[int]] = None,
            axis: OptAttrSetupType[eflr_types.AxisItem] = None,
            zones: OptAttrSetupType[ListOrTuple[eflr_types.ZoneItem]] = None,
            values: OptAttrSetupType[NestedList[Union[str, int, float]]] = None,
            set_name: Optional[str] = None,
            origin_reference: Optional[int] = None
    ) -> eflr_types.ParameterItem:
        """Create a parameter.

        'Parameter Objects (...) specify Parameters (constant or zoned) used in the acquisition and processing of data.
        Parameters may be scalar-valued or array-valued. When they are array-valued, the semantic meaning
        of the array dimensions is defined by the application.'

        Args:
            name                :   Name of the object.
            long_name           :   Description of the parameter.
            dimension           :   '[S]pecifies the array structure of a single value of the current Parameter'.
            axis                :   Axis associated with the parameter.
            zones               :   '[A] List of references to Zone Objects that specify mutually disjoint intervals
                                    over which the value of the current Parameter is constant. A Parameter may have
                                    different values in different zones. When this Attribute is present, the Parameter
                                    is said to be Zoned, and it is considered to be defined only in the zones
                                    specified by the Zones Attribute. It is considered to be undefined elsewhere.
                                    The Zone Objects referenced in this List must all have the same Domain Attribute
                                    Value. That is, a Parameter Object may only be zoned over a single domain.'
            values              :   '[A] List of Parameter values corresponding to the zones listed in the Zones
                                    Attribute. When the Parameter is Zoned, the number of Parameter values is the same
                                    as the number of zones referenced, and the kth Parameter value applies
                                    to the kth zone. When the Parameter is Unzoned, there is a single Parameter value
                                    in the Values Attribute.'
            set_name            :   Name of the ParameterSet this parameter should be added to.
            origin_reference    :   file_set_number of the Origin this record belongs to.

        Returns:
            A configured ParameterItem instance.
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

        `Path Objects specify which Channels in the Data Frames of a given Frame Type are combined to define part or all
        of a Data Path, and what variations in alignment exist.
        The Index of a Frame Type automatically and explicitly serves as a Locus component of any Data Path represented
        in the Frame Type whenever Frame Attribute INDEX-TYPE has one of the values angular-drift, borehole-depth,
        radial-drift, time, or vertical-depth.`
        (Note: the above-mentioned index-type values - 'angular-drift' etc. - are spelled in all-uppercase
        ('ANGULAR-DRIFT').)

        Args:
            name                    :   Name of the object.
            frame_type              :   '[R]eferences a Frame Object in the current Logical File and indicates the
                                        Frame Type in which the Channels of the current Path are recorded.'
            well_reference_point    :   '[R]eferences the Well-Reference-Point Object in the current Logical File
                                        that specifies the Well Reference Point for entities specified by the remaining
                                        Attributes of the Path Object.'
            value                   :   '[R]eferences a Channel Object that defines the Value Channel for the current
                                        Path. This may also be a List of references in case multiple Channels share
                                        exactly the same Path features described by the remaining recorded Attributes
                                        of the Path Object. It is permissible for the Value Channel also to be
                                        one of the Locus coordinates.'
            borehole_depth          :   '[S]pecifies the constant Borehole Depth coordinate for the current Path,
                                        or it references the Channel Object (...) that defines a Borehole Depth Channel
                                        for the current Path. This Attribute should not be present if the Frame Type
                                        for the current Path has an Index-Type Value of borehole-depth.'
            vertical_depth          :   '[S]pecifies the constant Vertical Depth coordinate for the current Path,
                                        or it references the Channel Object (...) that defines a Vertical Depth Channel
                                        for the current Path. This Attribute should not be present if the Frame Type
                                        for the current Path has an Index-Type Value of vertical-depth.'
            radial_drift            :   `[S]pecifies the constant Radial Drift coordinate for the current Path,
                                        or it references the Channel Object (...) that defines a Radial Drift Channel
                                        for the current Path. This Attribute should not be present if the Frame Type
                                        for the current Path has an Index-Type Value of radial-drift.`
            angular_drift           :   '[S]pecifies the constant Angular Drift coordinate for the current Path,
                                        or it references the Channel Object (...) that defines an Angular Drift Channel
                                        for the current Path. This Attribute should not be present if the Frame Type
                                        for the current Path has an Index-Type Value of angular-drift.'
            time                    :   '[S]pecifies the constant Time coordinate for the current Path,
                                        or it references the Channel Object (...) that defines a Time Channel
                                        for the current Path. This Attribute should not be present if the Frame Type
                                        for the current Path has an Index-Type Value of TIME.
                                        The Time coordinate represents an absolute date and time [or] elapsed time
                                        from the date and time specified in the Creation-Time Attribute
                                        of the Origin Object.'
            depth_offset            :   '[S]pecifies a Depth Offset, which indicates how much the Value Channel is
                                        "off depth". This is a special case and applies only when there is a recorded
                                        Borehole Depth Channel for the current Path. Specifically, if the recorded
                                        Borehole Depth for the current Path in a Frame is D and the known Borehole Depth
                                        is D' , then D = D' + Depth-Offset.'
            measure_point_offset    :   '[S]pecifies a Measure Point Offset, which indicates a fixed distance along
                                        Borehole Depth from the Value Channel’s Measure Point to a Data Reference Point
                                        (...). This is a special case that depends on the data acquisition model
                                        and applies only when there is a recorded Borehole Depth Channel
                                        for the current Path.
                                        If the Measure-Point-Offset Attribute is zero or absent, then the Time Channel
                                        for the current Path is explicitly related to the Value Channel.
                                        That is, in each Frame, Vi is sampled at Ti.
                                        If the Measure-Point-Offset Attribute is present and non-zero, then the Time
                                        Channel is instead explicitly related to the Data Reference Point,
                                        and is implicitly related to the Value Channel. In each Frame, Ti is the time
                                        that the Data Reference Point was at Di, which is the Frame’s Borehole Depth.
                                        The Value Channel sample Vi is still considered to be sampled at Di,
                                        but at a time different from Ti. The explicit Time for the Value Channel
                                        can be recovered using the knowledge that at time Ti when the Data Reference
                                        Point was at depth Di, the Value Channel Measure Point was at depth Di
                                        - Measure-Point-Offset.
                                        Typically, only a single Time Channel per Origin will be recorded in a Frame
                                        Type, the one explicitly associated with the Data Reference Point.'
            tool_zero_offset        :   '[T]he distance of the Data Reference Point for the current Path above
                                        the tool string’s Tool Zero Point. It may be positive or negative;
                                        it is frequently zero.
                                        Specifically, Data Reference Point = Tool Zero Point + Tool-Zero-Offset.'
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

        '[Each Process] describes a specific process or computation applied to input Objects to get output Objects.'

        Args:
            name                :   Name of the object.
            description         :   Description of the process.
            trademark_name      :   '[T]he name used by the Producer to refer to the process and its products.'
            version             :   '[T]he Producer’s software version of the process.'
            properties          :   '[P]roperties that apply to the output of the process as a result of the process.'
                                    See dlis_writer.utils.enums.PROPERTIES for allowed values.
            status              :   Status of the process; 'ABORTED', 'COMPLETE' or 'IN-PROGRESS'.
                                    '[T]he state of the process at the time that the Status Attribute was recorded.'
            input_channels      :   'Channels that are used directly by this Process.'
            output_channels     :   'Channels that are produced directly by this Process. The same CHANNEL Object
                                    should not appear in the OUTPUT-CHANNELS Attribute of more than one PROCESS Object.'
            input_computations  :   'Computations that are used directly by this Process.'
            output_computations :   'Computations that are produced directly by this Process. The same COMPUTATION
                                    Object should not appear in the OUTPUT-COMPUTATIONS Attribute of more than one
                                    PROCESS Object.'
            parameters          :   'Parameters that are used by the Process or that directly affect the operation
                                    of the Process'
            comments            :   '[I]nformation specific to the particular execution of the process
                                    (generally provided by the user).'
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

        'Splice Objects describe the process of concatenating two or more instances of a Channel
        (e.g., from different runs) to get a resultant spliced Channel.'

        Args:
            name                :   Name of the object.
            output_channel      :   '[R]eferences the Channel Object that represents the spliced Channel,
                                    i.e., the resultant of the splice operation. The spliced Channel may be implied
                                    by the Splice Object and need not actually exist. When the spliced Channel does
                                    exist, its Properties Attribute must include the "Spliced" flag.'
            input_channels      :   '[A] List of references to Channel Objects that represent the input Channels
                                    of the splice operation.'
            zones               :   '[A] List of references to Zone Objects. When not Absent, this Attribute must have
                                    the same number of Elements (...) as the Input-Channels Attribute.
                                    The k-th referenced Zone Object defines a zone in which the spliced Channel
                                    matches the values of the k-th referenced input Channel (allowing for possible
                                    differences in Representation Code and Units). The referenced Zone Objects
                                    must specify mutually-disjoint zones in the same domain, but the ordering
                                    of the zones is arbitrary.'
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

        'Tool Objects (...) specify ensembles of equipment that work together to provide specific measurements
        or services. Such combinations are more recognizable to the Consumer than are their individual pieces.
        A typical tool consists of a sonde and a cartridge and possibly some appendages such as centralizers
        and spacers. It is also possible to identify certain pieces or combinations of surface measuring equipment
        as tools.'

        Args:
            name                :   Name of the object.
            description         :   Description of the tool.
            trademark_name      :   '[T]he name used by the Producer to refer to the Tool.'
            generic_name        :   '[T]he name generally used within the industry to refer to tools of this type.'
            parts               :   A list of EquipmentItem objects, describing parts of the tool.
            status              :   Status of the tool: 1 or 0.
                                    '[I]ndicates whether the tool is enabled to provide information to the acquisition
                                    system or whether it has been disabled and is simply occupying space.'
            channels            :   A list of ChannelItem objects, describing data channels `produced directly
                                    by this Tool`. A Channel should not be used in more than one Tool.
            parameters          :   A list of ParameterItem objects `corresponding to Parameters that directly affect
                                    or reflect the operation of this Tool`.
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

        'Each well has a Well Reference Point (WRP) that defines the origin of the well’s spatial coordinate system.
        The Well Reference Point is a fixed point in space defined for each Origin. This point is defined relative
        to some permanent structure, such as ground level or mean sea level. It need not coincide with the permanent
        structure, but its vertical distance from the permanent structure must be stated. (...)
        Spatial coordinates of a well are depth, Radial Drift, and Angular Drift. Depth is defined in terms of
        Borehole Depth or Vertical Depth.'

        Args:
            name                        :   Name of the object.
            permanent_datum             :   '[S]pecifies a Permanent Datum, an entity or structure (e.g., Ground Level)
                                            from which vertical distance can be measured.'
            vertical_zero               :   '[S]pecifies Vertical Zero, a particular entity (e.g., Kelly Bushing)
                                            that corresponds to zero depth.'
            permanent_datum_elevation   :   '[T]he distance of the Permanent Datum above mean sea level. A negative
                                            value indicates that the Permanent Datum is below mean sea level.'
            above_permanent_datum       :   '[T]he distance of Vertical Zero above the Permanent Datum.
                                            The distance can be negative, which indicates that Vertical Zero is below
                                            the Permanent Datum.'
            magnetic_declination        :   '[T]he angle with vertex at the Well Reference Point determined by the line
                                            of direction to geographic north and the line of direction to magnetic
                                            north. A positive value indicates that magnetic north is east
                                            of geographic north. A negative value indicates that magnetic north is
                                            west of geographic north.'
            coordinate_1_name           :   '[T]he name of the first of three independent spatial coordinates, such as
                                            longitude or latitude or elevation, that can be used to locate
                                            the Well Reference Point.'
            coordinate_1_value          :   '[T]he numerical value of the [first] coordinate'.
            coordinate_2_name           :   '[T]he name of the second of three independent spatial coordinates
                                            that can be used to locate the Well Reference Point.'
            coordinate_2_value          :   '[T]he numerical value of the [second] coordinate'.
            coordinate_3_name           :   '[T]he name of a third independent spatial coordinate that can be used
                                            to locate the Well Reference Point.'
            coordinate_3_value          :   '[T]he numerical value of the [third] coordinate'.
            set_name                    :   Name of the WellReferencePointSet this item should be added to.
            origin_reference            :   file_set_number of the Origin this record belongs to.

        Note:
            'Traditionally the coordinates of a well are described by latitude, longitude, and elevation.
            This information can be represented in the Well-Reference-Point Object without using Coordinate-3-Name
            and Coordinate-3-Value. There are other coordinate systems in use, however, that do not use elevation
            and for which the third general coordinate is needed.'


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
        """Create a zone (ZoneItem) and add it to the DLIS.

        `Zone Objects specify single intervals in depth or time. Zone Objects are useful for associating other Objects
        or values with specific regions of a well or with specific time intervals.`

        Args:
            name                :   Name of the object.
            description         :   Description of the zone; arbitrary.
            domain              :   Domain of the zone.
                                    '[I]ndicates the type of interval'. One of:
                                        - 'BOREHOLE-DEPTH': 'along the borehole'
                                        - 'TIME': 'elapsed time'
                                        - 'VERTICAL-DEPTH': 'along the Vertical Generatrix'.
            maximum             :   '[T]he depth of the bottom (deepest part) of the zone or the latest time.
                                    This value is not considered to be part of the zone.
                                    When this Attribute is absent, the zone is considered to extend indefinitely
                                    in the direction corresponding to deepest or latest.'
            minimum             :   ' the depth of the top (shallowest part) of the zone or the earliest time.
                                    This value is considered to be part of the zone.
                                    When this Attribute is absent, the zone is considered to extend indefinitely
                                    in the direction corresponding to shallowest or earliest.'
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
        self._check_defining_origin_params()

    def _check_defining_origin_params(self) -> None:
        """Check that the file_id of the defining origin is the same as the ID of the header."""

        do = self.defining_origin
        if not do:
            raise RuntimeError("Origin not defined")

        fh_id = self.file_header.header_id

        if do.file_id.value is None:
            do.file_id.value = fh_id
        else:
            if do.file_id.value != fh_id:
                raise ValueError("'file_id' of the Defining Origin should be the same as the ID (header_id) "
                                 f"of the file header; got {repr(do.file_id.value)} and {repr(fh_id)}")

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
