import datetime
from typing import Any, Union, Optional
import numpy as np
import os
from timeit import timeit
from datetime import timedelta
import logging

from dlis_writer.utils.source_data_objects import DictInterface
from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.logical_record.eflr_types.axis import AxisObject, Axis
from dlis_writer.logical_record.eflr_types.channel import ChannelObject, Channel
from dlis_writer.logical_record.eflr_types.equipment import Equipment, EquipmentObject
from dlis_writer.logical_record.eflr_types.file_header import FileHeaderObject, FileHeader
from dlis_writer.logical_record.eflr_types.frame import FrameObject, Frame
from dlis_writer.logical_record.eflr_types.origin import OriginObject, Origin
from dlis_writer.logical_record.eflr_types.parameter import Parameter, ParameterObject
from dlis_writer.logical_record.eflr_types.splice import Splice, SpliceObject
from dlis_writer.logical_record.eflr_types.zone import Zone, ZoneObject
from dlis_writer.logical_record.collections.file_logical_records import FileLogicalRecords
from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.writer.writer import DLISWriter


logger = logging.getLogger(__name__)


kwargs_type = dict[str, Any]
number_type = Union[int, float]


class DLISFile:
    """Define the structure and contents of a DLIS and create a file based on the provided information."""

    def __init__(
            self,
            storage_unit_label: Optional[Union[StorageUnitLabel, kwargs_type]] = None,
            file_header: Optional[Union[FileHeaderObject, kwargs_type]] = None,
            origin: Optional[Union[OriginObject, kwargs_type]] = None
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
            self._sul = StorageUnitLabel(**({"set_identifier": "MAIN STORAGE UNIT"} | (storage_unit_label or {})))

        if isinstance(file_header, FileHeaderObject):
            self._file_header = file_header
        else:
            self._file_header = FileHeader.make_object(**({"name": "FILE HEADER"} | (file_header or {})))

        if isinstance(origin, OriginObject):
            self._origin = origin
        else:
            self._origin = Origin.make_object(**({"name": "ORIGIN", "file_set_number": 1} | (origin or {})))

        self._channels = []
        self._frames = []
        self._other = []

        self._data_dict = {}

    @property
    def storage_unit_label(self) -> StorageUnitLabel:
        """Storage Unit Label of the DLIS."""

        return self._sul

    @property
    def file_header(self) -> FileHeaderObject:
        """File header of the DLIS."""

        return self._file_header

    @property
    def origin(self) -> OriginObject:
        """Origin of the DLIS. Note: currently only adding a single origin is supported."""

        return self._origin

    @property
    def channels(self) -> list[ChannelObject]:
        """Channels defined for the DLIS."""

        return self._channels

    @property
    def frames(self) -> list[FrameObject]:
        """Frames defined for the DLIS."""

        return self._frames

    def add_axis(
            self,
            name: str,
            axis_id: str = None,
            coordinates: list[Union[int, float, str]] = None,
            spacing: number_type = None
    ) -> AxisObject:
        """Define an axis (AxisObject) and add it to the DLIS.

        Args:
            name        :   Name of the axis.
            axis_id     :   ID of the axis.
            coordinates :   List of coordinates of the axis.
            spacing     :   Spacing of the axis.
        """

        ax = Axis.make_object(
            name=name,
            axis_id=axis_id,
            coordinates=coordinates,
            spacing=spacing
        )

        self._other.append(ax)
        return ax

    def add_channel(
            self,
            name: str,
            data: np.ndarray,
            long_name: Optional[str] = None,
            properties: Optional[list[str]] = None,
            units: Optional[str] = None,
            axis: Optional[AxisObject] = None,
            minimum_value: Optional[float] = None,
            maximum_value: Optional[float] = None
    ) -> ChannelObject:
        """Define a channel (ChannelObject) and add it to the DLIS.

        Args:
            name            :   Name of the channel.
            data            :   Data associated with the channel.
            long_name       :   Description of the channel.
            properties      :   List of properties of the channel.
            units           :   Unit of the channel data.
            axis            :   Axis associated with the channel.
            minimum_value   :   Minimum value of the channel data.
            maximum_value   :   Maximum value of the channel data.

        Returns:
            A configured ChannelObject instance, which is already added to the DLIS (but not to any frame).
        """

        if not isinstance(data, np.ndarray):
            raise ValueError(f"Expected a numpy.ndarray, got a {type(data)}")

        ch = Channel.make_object(
            name,
            long_name=long_name,
            properties=properties,
            units=units,
            axis=axis,
            minimum_value=minimum_value,
            maximum_value=maximum_value
        )
        # skipping repr code, dimension, and element limit because they will be determined from the data
        # skipping dataset_name - using channel name instead

        self._channels.append(ch)
        self._data_dict[ch.dataset_name] = data  # channel's dataset_name is the provided dataset_name or channel's name

        return ch

    def add_equipment(
            self,
            name: str,
            trademark_name: str = None,
            status: int = None,
            eq_type: str = None,
            serial_number: str = None,
            location: str = None,
            height: number_type = None,
            length: number_type = None,
            minimum_diameter: number_type = None,
            maximum_diameter: number_type = None,
            volume: number_type = None,
            weight: number_type = None,
            hole_size: number_type = None,
            pressure: number_type = None,
            temperature: number_type = None,
            vertical_depth: number_type = None,
            radial_drift: number_type = None,
            angular_drift: number_type = None
    ) -> EquipmentObject:
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

        Returns:
            A configured EquipmentObject instance.
        """

        eq = Equipment.make_object(
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
            angular_drift=angular_drift
        )

        self._other.append(eq)
        return eq

    def add_frame(
            self,
            name: str,
            channels: Union[list[ChannelObject], tuple[ChannelObject, ...]],
            description: Optional[str] = None,
            index_type: Optional[str] = None,
            direction: Optional[str] = None,
            spacing: Optional[Union[int, float]] = None,
            encrypted: Optional[int] = None,
            index_min: Optional[Union[int, float]] = None,
            index_max: Optional[Union[int, float]] = None
    ) -> FrameObject:
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

        if not all(isinstance(c, ChannelObject) for c in channels):
            raise TypeError(f"Expected a list of ChannelObject instances; "
                            f"got types: {', '.join(str(type(c)) for c in channels)}")

        fr = Frame.make_object(
            name,
            channels=channels,
            description=description,
            index_type=index_type,
            direction=direction,
            spacing=spacing,
            encrypted=encrypted,
            index_min=index_min,
            index_max=index_max
        )

        self._frames.append(fr)
        return fr

    def add_parameter(
            self,
            name: str,
            long_name: str = None,
            dimension: list[int] = None,
            axis: AxisObject = None,
            zones: Union[list[ZoneObject], tuple[ZoneObject, ...]] = None,
            values: Union[list[int], list[float], list[str]] = None
    ) -> ParameterObject:
        """Create a parameter.

        Args:
            name        :   Name of the parameter.
            long_name   :   Description of the parameter.
            dimension   :   Dimension of the parameter.
            axis        :   Axis associated with the parameter.
            zones       :   Zones the parameter is defined for.
            values      :   Values of the parameter - numerical or textual.

        Returns:
            A configured ParameterObject instance.
        """

        p = Parameter.make_object(
            name=name,
            long_name=long_name,
            dimension=dimension,
            axis=axis,
            zones=zones,
            values=values
        )

        self._other.append(p)
        return p

    def add_splice(
            self,
            name: str,
            output_channel: ChannelObject = None,
            input_channels: Union[list[ChannelObject], tuple[ChannelObject, ...]] = None,
            zones: Union[list[ZoneObject], tuple[ZoneObject, ...]] = None
    ) -> SpliceObject:
        """Create a splice object.

        Args:
            name            :   Name of the splice.
            output_channel  :   Output of the splice.
            input_channels  :   Input of the splice.
            zones           :   Zones the splice is defined for.

        Returns:
            A configured splice.
        """

        sp = Splice.make_object(
            name=name,
            output_channel=output_channel,
            input_channels=input_channels,
            zones=zones
        )
        self._other.append(sp)
        return sp

    def add_zone(
            self,
            name: str,
            description: str = None,
            domain: str = None,
            maximum: Union[datetime.datetime, int, float] = None,
            minimum: Union[datetime.datetime, int, float] = None
    ) -> ZoneObject:
        """Create a zone (ZoneObject) and add it to the DLIS.

        Args:
            name        :   Name of the zone.
            description :   Description of the zone.
            domain      :   Domain of the zone. One of: 'BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH'.
            maximum     :   Maximum of the zone.
            minimum     :   Minimum of the zone.

        Note:
            Maximum and minimum should be instances of datetime.datetime if the domain is TIME. In other cases,
            they should be floats.

        Returns:
            A configured zone, added to the DLIS.
        """

        z = Zone.make_object(
            name=name,
            description=description,
            domain=domain,
            maximum=maximum,
            minimum=minimum
        )

        self._other.append(z)
        return z

    def _make_multi_frame_data(self, fr: FrameObject, **kwargs) -> MultiFrameData:
        """Create a MultiFrameData object, containing the frame and associated data, generating FrameData instances."""

        name_mapping = {ch.name: ch.dataset_name for ch in fr.channels.value}
        data_object = DictInterface(self._data_dict, mapping=name_mapping)
        fr.setup_from_data(data_object)
        return MultiFrameData(fr, data_object, **kwargs)

    def make_file_logical_records(self, chunk_size: Optional[int] = None) -> FileLogicalRecords:
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
        flr.add_frame_data_objects(*(self._make_multi_frame_data(fr, chunk_size=chunk_size) for fr in self._frames))
        flr.add_logical_records(*get_parents(self._other))

        return flr

    def write(self, dlis_file_name: Union[str, os.PathLike[str]], visible_record_length: int = 8192,
              input_chunk_size: Optional[int] = None, output_chunk_size: number_type = 2**32):
        """Create a DLIS file form the current specifications.

        Args:
            dlis_file_name          :   Name of the file to be created.
            visible_record_length   :   Maximal length of visible records to be created in the file.
            input_chunk_size        :   Size of the chunks (in rows) in which input data will be loaded to be processed.
            output_chunk_size       :   Size of the buffers accumulating file bytes before file write action is called.
        """

        def timed_func():
            """Perform the action of creating a DLIS file.

            This function is used in a timeit call to time the file creation.
            """

            dlis_file = DLISWriter(visible_record_length=visible_record_length)
            logical_records = self.make_file_logical_records(chunk_size=input_chunk_size)
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
