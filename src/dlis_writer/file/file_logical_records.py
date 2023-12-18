import typing
import logging

from dlis_writer.file import MultiFrameData
from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.logical_record.eflr_types import *
from dlis_writer.logical_record.iflr_types.no_format_frame_data import NoFormatFrameData
from dlis_writer.logical_record.core.eflr import EFLRSet


logger = logging.getLogger(__name__)


class FileLogicalRecords:
    """Collection of logical records to constitute a DLIS file."""

    def __init__(self, sul: StorageUnitLabel, fh: FileHeaderSet, orig: OriginSet):
        """Initialise FileLogicalRecords object.

        Args:
            sul     :   Instance of StorageUnitLabel.
            fh      :   Instance of FileHeader EFLR.
            orig    :   Instance of Origin EFLR.
        """

        self._check_type(sul, StorageUnitLabel)
        self._check_type(fh, FileHeaderSet)
        self._check_type(orig, OriginSet)

        self._storage_unit_label = sul
        self._file_header = fh
        self._origin = orig

        self._channels: list[ChannelSet] = []
        self._frames: list[FrameSet] = []
        self._frame_data_objects: list[MultiFrameData] = []
        self._other_logical_records: list[typing.Union[EFLRSet, NoFormatFrameData]] = []

    def set_origin_reference(self, value: int):
        """Set 'origin_reference' of all logical records in the collection (except SUL) to the provided value."""

        self._file_header.origin_reference = value
        self._origin.origin_reference = value

        for ch in self._channels:
            ch.origin_reference = value

        for fr in self._frames:
            fr.origin_reference = value

        for lr in self._other_logical_records:
            if not isinstance(lr, NoFormatFrameData):
                lr.origin_reference = value

        for fdo in self._frame_data_objects:
            fdo.set_origin_reference(value)

    @property
    def origin(self) -> OriginSet:
        """Origin EFLR of the collection."""

        return self._origin

    @property
    def header_records(self) -> tuple[StorageUnitLabel, FileHeaderSet, OriginSet]:
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
    def _check_types(values: typing.Iterable, expected_type: typing.Union[type, tuple[type, ...]]):
        """Check that the provided values are all instances of the expected type.

        Args:
            values          :   Values to be checked.
            expected_type   :   Expected type of the value.

        Raises:
            TypeError   :   If any of the values is not an instance of the expected type.
        """

        if not all(isinstance(v, expected_type) for v in values):
            if not isinstance(expected_type, tuple):
                expected_type = expected_type,
            raise TypeError(f"Expected only {' / '.join(t.__name__ for t in expected_type)} objects; "
                            f"got {', '.join(type(v).__name__ for v in values)}")

    def add_channels(self, *channels: ChannelSet):
        """Add Channel logical records to the collection."""

        self._check_types(channels, ChannelSet)
        self._channels.extend(channels)

    @property
    def frames(self) -> list[FrameSet]:
        """Frame logical records added to the collection."""

        return self._frames

    def add_frames(self, *frames: FrameSet):
        """Add Frame logical records to the collection."""

        self._check_types(frames, FrameSet)
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

    def add_logical_records(self, *lrs: typing.Union[EFLRSet, NoFormatFrameData]):
        """Add other EFLR objects (other than Channel, Frame, Origin, FileHeader) to the collection."""

        self._check_types(lrs, (EFLRSet, NoFormatFrameData))
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

        def check(eflr: EFLRSet, exactly_one: bool = False):
            """Check that at least/exactly one EFLRObject is defined for the provided EFLR."""

            names = [o.name for o in eflr.get_all_eflr_items()]
            verify_n(names, eflr.__class__.__name__, exactly_one=exactly_one)

        def check_list(eflr_list: list[EFLRSet], class_name: str):
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
