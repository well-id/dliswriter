from typing_extensions import Self
import typing
from configparser import ConfigParser
import logging

from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.logical_record.eflr_types import *
from dlis_writer.logical_record.eflr_types.frame import FrameItem
from dlis_writer.logical_record.eflr_types.origin import OriginItem
from dlis_writer.logical_record.eflr_types.file_header import FileHeaderItem
from dlis_writer.logical_record.core.eflr import EFLRTable
from dlis_writer.utils.source_data_wrappers import SourceDataWrapper


logger = logging.getLogger(__name__)


class FileLogicalRecords:
    """Collection of logical records to constitute a DLIS file."""

    def __init__(self, sul: StorageUnitLabel, fh: FileHeaderTable, orig: OriginTable):
        """Initialise FileLogicalRecords object.

        Args:
            sul     :   Instance of StorageUnitLabel.
            fh      :   Instance of FileHeader EFLR.
            orig    :   Instance of Origin EFLR.
        """

        self._check_type(sul, StorageUnitLabel)
        self._check_type(fh, FileHeaderTable)
        self._check_type(orig, OriginTable)

        self._storage_unit_label = sul
        self._file_header = fh
        self._origin = orig

        self._channels: list[ChannelTable] = []
        self._frames: list[FrameTable] = []
        self._frame_data_objects: list[MultiFrameData] = []
        self._other_logical_records: list[EFLRTable] = []

    def set_origin_reference(self, value: int):
        """Set 'origin_reference' of all logical records in the collection (except SUL) to the provided value."""

        self._file_header.origin_reference = value
        self._origin.origin_reference = value

        for ch in self._channels:
            ch.origin_reference = value

        for fr in self._frames:
            fr.origin_reference = value

        for lr in self._other_logical_records:
            lr.origin_reference = value

        for fdo in self._frame_data_objects:
            fdo.set_origin_reference(value)

    @property
    def origin(self) -> OriginTable:
        """Origin EFLR of the collection."""

        return self._origin

    @property
    def header_records(self) -> tuple[StorageUnitLabel, FileHeaderTable, OriginTable]:
        """Header records of the collection: StorageUnitLabel, FileHeader, and Origin."""

        return self._storage_unit_label, self._file_header, self._origin

    @staticmethod
    def _check_type(value: typing.Any, expected_type: type):
        """Check that the provided value is an instance of the expected type.

        Args:
            value           :   Value to be checked.
            expected_type   :   Expected type of the value.

        Raises:
            TypeError   :   If the value is not an instance of the expected type.
        """

        if not isinstance(value, expected_type):
            raise TypeError(f"Expected an instance of {expected_type.__name__}; got {type(value)}")

    @staticmethod
    def _check_types(values: typing.Iterable, expected_type: type):
        """Check that the provided values are all instances of the expected type.

        Args:
            values          :   Values to be checked.
            expected_type   :   Expected type of the value.

        Raises:
            TypeError   :   If any of the values is not an instance of the expected type.
        """

        if not all(isinstance(v, expected_type) for v in values):
            raise TypeError(f"Expected only {expected_type.__name__} objects; "
                            f"got {', '.join(type(v).__name__ for v in values)}")

    def add_channels(self, *channels: ChannelTable):
        """Add Channel logical records to the collection."""

        self._check_types(channels, ChannelTable)
        self._channels.extend(channels)

    @property
    def frames(self) -> list[FrameTable]:
        """Frame logical records added to the collection."""

        return self._frames

    def add_frames(self, *frames: FrameTable):
        """Add Frame logical records to the collection."""

        self._check_types(frames, FrameTable)
        self._frames.extend(frames)

    @property
    def frame_data_objects(self) -> list[MultiFrameData]:
        """MultiFrameData objects (collections of FrameData objects) added to the collection."""

        return self._frame_data_objects

    def add_frame_data_objects(self, *fds: MultiFrameData):
        """Add MultiFrameData objects (collections of FrameData objects) to the collection."""

        self._check_types(fds, MultiFrameData)
        self._frame_data_objects.extend(fds)

    def __len__(self) -> int:
        """Calculate current number of individual logical records defined in the collection.

        Adds up the numbers of all channels, frames, and other explicitly formatted logical records.
        Takes into account the storage unit label, file header, and origin.
        Adds the lengths of all added MultiFrameData objects - i.e. FrameData records that will be generated from them.
        """

        def get_len(lr_list):
            return sum(lr.n_items for lr in lr_list)

        len_channels = get_len(self._channels)                          # number of Channel EFLRs
        len_frames = get_len(self._frames)                              # number of Frame EFLRs
        len_other = get_len(self._other_logical_records)                # number of any other defined EFLRs
        len_data = sum(len(mfd) for mfd in self.frame_data_objects)     # number of FrameData objects to be generated
        return len(self.header_records) + len_channels + len_frames + len_data + len_other  # total length

    def __iter__(self):
        """Iterate over all logical records defined in the object.

        Yields: StorageUnitLabel, EFLR, and IFLR objects.
        """

        yield from self.header_records
        yield from self._channels
        yield from self._frames

        for fdo in self._frame_data_objects:  # list of MultiFrameData
            yield from fdo  # FrameData objects

        yield from self._other_logical_records

    def add_logical_records(self, *lrs: EFLRTable):
        """Add other EFLR objects (other than Channel, Frame, Origin, FileHeader) to the collection."""

        self._check_types(lrs, EFLRTable)
        self._other_logical_records.extend(lrs)

    def check_objects(self):
        """Check that the collection contains all required objects in the required (min/max) numbers.

        Raises:
            RuntimeError    :   If not enough or too many of any of the required object types are defined.
        """

        def verify_n(names: list[str], class_name: str, exactly_one: bool = False):
            """Check that at least one (or exactly one, if the corresponding flag is True) objects are defined.

            Args:
                names       :   List of names of objects defined for the given type of EFLR.
                class_name  :   Name of the EFLR class (for error messages)
                exactly_one :   If True, raise an error if more than 1 object of the given type is defined.
            """

            n = len(names)
            if not n:
                raise RuntimeError(f"No {class_name}Object defined")

            if exactly_one and n > 1:
                raise RuntimeError(f"Expected exactly one {class_name}Object, got {n} with names: "
                                   f"{', '.join(repr(n) for n in names)}")

        def check(eflr: EFLRTable, exactly_one: bool = False):
            """Check that at least/exactly one EFLRObject is defined for the provided EFLR."""

            names = [o.name for o in eflr.get_all_eflr_items()]
            verify_n(names, eflr.__class__.__name__, exactly_one=exactly_one)

        def check_list(eflr_list: list[EFLRTable], class_name: str):
            """Check that at least one EFLRObject is defined across the list of EFLRs of the given type."""

            names: list[str] = []
            for eflr in eflr_list:
                names.extend(o.name for o in eflr.get_all_eflr_items())
            verify_n(names, class_name)

        check(self._file_header, exactly_one=True)
        check(self._origin)
        check_list(self._frames, "Frame")
        check_list(self._channels, "Channel")

        self._check_channels()

    def _check_channels(self):
        """Check that all defined ChannelObject instances are assigned to at least one FrameObject.

        Issues a warning in the logs if the condition is not fulfilled (possible issues with opening file in DeepView).
        """

        channels_in_frames = set()
        for frm in self._frames:
            for frame_object in frm.get_all_eflr_items():
                channels_in_frames |= set(frame_object.channels.value)

        for ch in self._channels:
            for channel_object in ch.get_all_eflr_items():
                if channel_object not in channels_in_frames:
                    logger.warning(f"{channel_object} has not been added to any frame; "
                                   f"this might cause issues with opening the produced DLIS file in some software")

    @staticmethod
    def _make_frame_and_data(config: ConfigParser, data: SourceDataWrapper, key: str = 'Frame',
                             chunk_size: typing.Optional[int] = None) \
            -> MultiFrameData:
        """Define a FrameObject and a corresponding MultiFrameData based on the provided config information.

        Args:
            config      :   Object containing information about the frame and other logical records.
            data        :   Wrapper for numerical data.
            key         :   Name of the frame object in the config (key of the respective section).
            chunk_size  :   Size of the chunks in which the input data will be loaded when iterating over FrameData
                            objects included in the frame.

        Returns:
            MultiFrameData object, containing the information on the frame and frame data records.
        """

        frame_object: FrameItem = FrameTable.make_eflr_item_from_config(config, key=key)

        if frame_object.channels.value:
            frame_object.setup_from_data(data)
            ch = f'with channels: {", ".join(c.name for c in frame_object.channels.value)}'
        else:
            ch = "(no channels defined)"
        logger.info(f'Preparing frames for {data.n_rows} rows {ch}')

        return MultiFrameData(frame_object, data, chunk_size=chunk_size)

    @classmethod
    def from_config_and_data(cls, config: ConfigParser, data: SourceDataWrapper,
                             chunk_size: typing.Optional[int] = None) -> Self:
        """Create a FileLogicalRecords object from a config object and data.

        Args:
            config      :   Object containing information about the logical records to be included in the file.
            data        :   Wrapper for numerical data.
            chunk_size  :   Size of the chunks in which the input data will be loaded when iterating over FrameData
                            objects included in the frame.

        Returns:
            FileLogicalRecords: a configured instance of the class.
        """

        file_header_object: FileHeaderItem = FileHeaderTable.make_eflr_item_from_config(config)
        origin_object: OriginItem = OriginTable.make_eflr_item_from_config(config)

        obj = cls(
            sul=StorageUnitLabel.make_from_config(config),
            fh=file_header_object.parent,
            orig=origin_object.parent
        )

        channels = ChannelTable.make_all_eflr_items_from_config(config)

        frame_keys = (key for key in config.sections() if key.startswith('Frame-') or key == 'Frame')
        frame_and_data_objects = [
            cls._make_frame_and_data(config, data, key=key, chunk_size=chunk_size) for key in frame_keys
        ]

        logger.info(f"Adding Channels: {', '.join(ch.name for ch in channels)} to the file")
        obj.add_channels(*(set(c.parent for c in channels)))

        for multi_frame_data in frame_and_data_objects:
            fr = multi_frame_data.frame
            logger.info(f"Adding {fr} and {len(multi_frame_data)} FrameData objects to the file")
            if fr.parent not in obj.frames:
                obj.add_frames(fr.parent)
            obj.add_frame_data_objects(multi_frame_data)

        other_classes = [c for c in eflr_types if c not in (ChannelTable, FrameTable, OriginTable, FileHeaderTable)]

        for c in other_classes:
            objects = c.make_all_eflr_items_from_config(config, get_if_exists=True)
            if not objects:
                logger.debug(f"No instances of {c.__name__} defined")
            else:
                logger.info(f"Adding {c.__name__}(s): {', '.join(o.name for o in objects)} to the file")
                obj.add_logical_records(*set(o.parent for o in objects))

        return obj
