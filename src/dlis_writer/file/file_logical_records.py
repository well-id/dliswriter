import typing
import logging

from dlis_writer.file import MultiFrameData
from dlis_writer.logical_record.misc import StorageUnitLabel
from dlis_writer.logical_record import eflr_types
from dlis_writer.logical_record.iflr_types.no_format_frame_data import NoFormatFrameData
from dlis_writer.logical_record.core.eflr import EFLRSet


logger = logging.getLogger(__name__)


class FileLogicalRecords:
    """Collection of logical records to constitute a DLIS file."""

    def __init__(self, sul: StorageUnitLabel, fh: eflr_types.FileHeaderSet, orig: eflr_types.OriginSet) -> None:
        """Initialise FileLogicalRecords object.

        Args:
            sul     :   Instance of StorageUnitLabel.
            fh      :   Instance of FileHeader EFLR.
            orig    :   Instance of Origin EFLR.
        """

        self._check_type(sul, StorageUnitLabel)
        self._check_type(fh, eflr_types.FileHeaderSet)
        self._check_type(orig, eflr_types.OriginSet)

        self._storage_unit_label = sul
        self._file_header = fh
        self._origin = orig

        self._channels: list[eflr_types.ChannelSet] = []
        self._frames: list[eflr_types.FrameSet] = []
        self._frame_data_objects: list[MultiFrameData] = []
        self._other_logical_records: list[typing.Union[EFLRSet, NoFormatFrameData]] = []

    def set_origin_reference(self, value: int) -> None:
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
    def origin(self) -> eflr_types.OriginSet:
        """Origin EFLR of the collection."""

        return self._origin

    @property
    def header_records(self) -> tuple[StorageUnitLabel, eflr_types.FileHeaderSet, eflr_types.OriginSet]:
        """Header records of the collection: StorageUnitLabel, FileHeader, and Origin."""

        return self._storage_unit_label, self._file_header, self._origin

    @staticmethod
    def _check_type(value: typing.Any, expected_type: type) -> None:
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
    def _check_types(values: typing.Iterable, expected_type: typing.Union[type, tuple[type, ...]]) -> None:
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

    def add_channels(self, *channels: eflr_types.ChannelSet) -> None:
        """Add Channel logical records to the collection."""

        self._check_types(channels, eflr_types.ChannelSet)
        self._channels.extend(channels)

    @property
    def frames(self) -> list[eflr_types.FrameSet]:
        """Frame logical records added to the collection."""

        return self._frames

    def add_frames(self, *frames: eflr_types.FrameSet) -> None:
        """Add Frame logical records to the collection."""

        self._check_types(frames, eflr_types.FrameSet)
        self._frames.extend(frames)

    @property
    def frame_data_objects(self) -> list[MultiFrameData]:
        """MultiFrameData objects (collections of FrameData objects) added to the collection."""

        return self._frame_data_objects

    def add_frame_data_objects(self, *fds: MultiFrameData) -> None:
        """Add MultiFrameData objects (collections of FrameData objects) to the collection."""

        self._check_types(fds, MultiFrameData)
        self._frame_data_objects.extend(fds)

    def __len__(self) -> int:
        """Calculate current number of individual logical records defined in the collection.

        Adds up the numbers of all channels, frames, and other explicitly formatted logical records.
        Takes into account the storage unit label, file header, and origin.
        Adds the lengths of all added MultiFrameData objects - i.e. FrameData records that will be generated from them.
        """

        def get_len(lr_list: list) -> int:
            return sum(lr.n_items for lr in lr_list)

        len_channels = get_len(self._channels)                          # number of Channel EFLRs
        len_frames = get_len(self._frames)                              # number of Frame EFLRs
        len_other = get_len(self._other_logical_records)                # number of any other defined EFLRs
        len_data = sum(len(mfd) for mfd in self.frame_data_objects)     # number of FrameData objects to be generated
        return len(self.header_records) + len_channels + len_frames + len_data + len_other  # total length

    def __iter__(self) -> typing.Generator:
        """Iterate over all logical records defined in the object.

        Yields: StorageUnitLabel, EFLR, and IFLR objects.
        """

        yield from self.header_records
        yield from self._channels
        yield from self._frames

        for fdo in self._frame_data_objects:  # list of MultiFrameData
            yield from fdo  # FrameData objects

        yield from self._other_logical_records

    def add_logical_records(self, *lrs: typing.Union[EFLRSet, NoFormatFrameData]) -> None:
        """Add other EFLR objects (other than Channel, Frame, Origin, FileHeader) to the collection."""

        self._check_types(lrs, (EFLRSet, NoFormatFrameData))
        self._other_logical_records.extend(lrs)
