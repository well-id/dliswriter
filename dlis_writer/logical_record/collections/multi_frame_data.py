import typing
from typing_extensions import Self

from dlis_writer.logical_record.eflr_types.frame import FrameObject
from dlis_writer.logical_record.iflr_types import FrameData
from dlis_writer.utils.source_data_objects import SourceDataObject


class MultiFrameData:
    """Create a generator for FrameData objects with additional metadata and functionalities.

    Iterate over an instance of MultiFrameData to yield consecutive instances of FrameData according to the provided
    SourceDataObject (specifying numerical data, channel names, data types etc.)
    """

    def __init__(self, frame: FrameObject, data: SourceDataObject, chunk_size: typing.Optional[int] = None):
        """Initialise MultiFrameData object.

        Args:
            frame       :   FrameObject instance the data refer to.
            data        :   Data (with basic metadata) to be included.
            chunk_size  :   Size (in number of rows) of chunks in which source data should be loaded when iterated over.
        """

        super().__init__()

        self._check_type(frame, FrameObject)
        self._check_type(data, SourceDataObject)
        self._check_type(chunk_size, int, type(None))

        frame_channel_names = tuple(c.name for c in frame.channels.value)
        data_channel_names = data.dtype.names
        if frame_channel_names != data_channel_names:
            raise ValueError(f"Channel names in data {data_channel_names} "
                             f"do not match channels defined in the frame {frame_channel_names}")

        self._data_source = data
        self._frame = frame

        self._origin_reference: typing.Union[int, None] = None

        self._chunk_rows = chunk_size
        self._i = 0  # keep track of current frame number during iteration
        self._data_item_generator = None

    @staticmethod
    def _check_type(value: typing.Any, *expected_types: type):
        """Check that value is an instance of the expected type. If not, raise a TypeError."""

        if not isinstance(value, expected_types):
            tp = '/'.join(t.__name__ for t in expected_types)
            raise TypeError(f"Expected an instance of {tp}; got {type(value)}: {value}")

    @property
    def frame(self) -> FrameObject:
        """FrameObject the data (and FrameData objects) belong to."""

        return self._frame

    def set_origin_reference(self, value: int):
        """Store origin reference so that it is assigned to every FrameData object at its creation later on."""

        self._origin_reference = value

    def __len__(self) -> int:
        """Number of data rows (= number of FrameData objects that can be created from the provided data)."""

        return self._data_source.n_rows

    def __iter__(self) -> Self:
        """Set up iteration over FrameData objects (to be) defined based on the data."""

        self._i = 0
        self._data_item_generator = self._data_source.make_chunked_generator(chunk_rows=self._chunk_rows)
        return self

    def __next__(self) -> FrameData:
        """Return a next FrameData object in the iteration."""

        if not self._data_item_generator:
            raise RuntimeError("Iteration has not been defined")

        if self._i >= self._data_source.n_rows:
            raise StopIteration

        self._i += 1

        return FrameData(
            frame=self._frame,
            frame_number=self._i,
            slots=next(self._data_item_generator),
            origin_reference=self._origin_reference
        )
