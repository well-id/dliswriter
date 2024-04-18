import logging
from progressbar import progressbar    # type: ignore  # untyped library
from typing import Optional, Sequence
from pathlib import Path

from dliswriter.utils.internal_enums import RepresentationCode
from dliswriter.utils.types import file_name_type, number_type, bytes_type
from dliswriter.logical_record.misc import StorageUnitLabel

logger = logging.getLogger(__name__)


class ByteWriter:
    """Write bytes to DLIS file."""

    def __init__(self, filename: file_name_type):
        """Initialise DLISFileWriter.

        Args:
            filename    :   Name of the file the bytes should be written to.
        """

        self._filename = filename
        self._append = False  # changes to True in first call of write_bytes
        self._total_size = 0

    @property
    def filename(self) -> file_name_type:
        """Name of the file being written."""

        return self._filename

    @property
    def total_size(self) -> int:
        """Number of bytes which have been written into the file."""

        return self._total_size

    def write_bytes(self, bts: bytes_type, size: Optional[int] = None) -> None:
        """Write (in 'wb' or 'ab' mode, as needed) the bytes into the file.

        Args:
            bts     :   Bytes to be written to the file.
            size    :   Number of bytes to be written. If not provided, it is calculated from bts.

        Note:
            For performance purposes, the provided size is not checked against the length of the bytes.
        """

        mode = 'ab' if self._append else 'wb'

        logger.debug("Writing bytes to file")
        with open(self._filename, mode) as f:
            f.write(bts)

        self._append = True  # in the future calls, append bytes to the file
        self._total_size += (size or len(bts))


class BufferedOutput:
    """Provide an automatised buffered interface for storing bytes into a file.

    Collect output bytes in a buffer of predefined size. Once buffer is full*, send the buffer contents to the
    file writer object to be stored, and prepare a new, empty buffer to collect more bytes.
    * the storing takes place when the space in the buffer is not enough to accept the provided sequence of bytes.

    Note:
        When last bytes have been passed to the buffer, it is necessary to explicitly call 'pass_bytes_to_writer'
        in order to send the bytes remaining in the buffer to the file writer.
    """

    def __init__(self, size: int, writer: ByteWriter):
        """Initialise BufferedOutput object.

        Args:
            size    :   Size of the buffer.
            writer  :   File writer object.
        """

        self._bts = bytearray(size)  #: the buffer
        self._filled_size = 0  #: how many bytes are in the current buffer
        self._buffer_size = size  #: size of the output buffer (needed when setting up a new one)

        self._writer = writer  #: file writer object

    def add_bytes(self, bts: bytes_type, size: Optional[int] = None) -> None:
        """Add bytes to the current output buffer.

        If the bytes would not fit in the current output buffer, send the currently kept bytes to the file writer,
        set up a clean output buffer, and add the new bytes there.

        Args:
            bts     :   Bytes to be added to the output buffer.
            size    :   Number of bytes to be added. If not provided, it is calculated from bts.

        Note:
            For performance purposes, the provided size is not checked against the length of the bytes.
        """

        size = size or len(bts)
        new_size = self._filled_size + size

        if new_size > self._buffer_size:
            self.pass_bytes_to_writer()  # also sets up a new output buffer
            logger.debug(f"Making new output chunk; current total output size is {self._writer.total_size}")
            new_size = size

        self._bts[self._filled_size:new_size] = bts
        self._filled_size = new_size

    def pass_bytes_to_writer(self) -> None:
        """Send the currently kept bytes to the file writer. Set up a new, empty output buffer."""

        self._writer.write_bytes(self._bts[:self._filled_size], self._filled_size)

        # set up a new output buffer
        self._bts = bytearray(self._buffer_size)
        self._filled_size = 0


class DLISWriter:
    """Create a DLIS file given data and structure information (specification of logical records)."""

    def __init__(self, filename: file_name_type, visible_record_length: int = 8192):
        """Initialise DLISFile object.

        Args:
            filename                :   Name of the file to be created. Note: at this point, no file name / directory
                                        checks (file already exists / directory write access / etc.) are performed.

            visible_record_length   :   Maximum allowed length of visible records (physical file units) in the created
                                        file. Expressed in bytes.
        """

        self._byte_writer = ByteWriter(filename)

        self._check_visible_record_length(visible_record_length)
        self._visible_record_length: int = visible_record_length  #: Maximum allowed visible record length, in bytes

        # format version is a required part of each visible record and is fixed for a given version of the standard
        self._fmt_version = RepresentationCode.USHORT.convert(255) + RepresentationCode.USHORT.convert(1)

        # flag set to True as soon as a StorageUnitLabel is written to the file (through write_storage_unit_label);
        # SUL must be the first element of the file
        self._sul_written = False

    @staticmethod
    def _check_visible_record_length(vrl: int) -> None:
        """Check the type and value of visible record length against several criteria."""

        if not isinstance(vrl, int):
            raise TypeError(f"Visible record length must be an integer; got {type(vrl)}")

        if vrl < 20:
            raise ValueError("Visible record length must be at least 20 bytes")

        if vrl > 16384:
            raise ValueError("Visible record length cannot be larger than 16384 bytes")

        if vrl % 2:
            raise ValueError("Visible record length must be an even number")

    def _make_visible_record(self, body: bytes_type, size: Optional[int] = None) -> bytes:
        """Create a visible record (physical DLIS unit) from the provided body bytes.

        Args:
            body    :   Bytes to create the visible record from.
            size    :   Number of bytes in the body. If not provided, it is calculated from the body object.

        Returns:
            Created visible record (provided body bytes preceded by header bytes) as a bytes object.

        Note:
            For performance purposes, the provided size is not checked against the length of the body bytes.
        """

        if size is None:
            size = len(body)

        size += 4  # 4 header bytes will be added

        if size > self._visible_record_length:
            raise ValueError(f"VR length is too large; got {size}, max is {self._visible_record_length}")

        return RepresentationCode.UNORM.convert(size) + self._fmt_version + body

    def _check_output_chunk_size(self, output_chunk_size: number_type) -> None:
        """Check output chunk size type (integer or float with zero decimal part) and value (>= max VR length)."""

        if not isinstance(output_chunk_size, (int, float)):
            raise TypeError(f"Output chunk size must be a number; got {type(output_chunk_size)}")

        if output_chunk_size % 1:
            raise ValueError(f"Output chunk size must be an integer; got {output_chunk_size}")

        if output_chunk_size < self._visible_record_length:
            raise ValueError(f"Output chunk size cannot be smaller than max visible record length "
                             f"(= {self._visible_record_length}); got {output_chunk_size}")

    def write_storage_unit_label(self, sul: StorageUnitLabel) -> None:
        """Convert a Storage Unit Label to bytes and write them into the file.

        Unlike other, 'proper' logical records, SUL should not be wrapped in a visible record structure,
        but instead written to the file as-is.
        """

        logger.info("Writing Storage Unit Label bytes to the file")
        self._byte_writer.write_bytes(sul.represent_as_bytes().bts)
        self._sul_written = True

    def write_logical_records(self, logical_records: Sequence, output_chunk_size: Optional[number_type]) -> None:
        """Write the provided logical records to the file.

        Note: write_storage_unit_label MUST be called BEFORE calling this method.
        Otherwise, a RuntimeError is raised.

        Args:
            logical_records     :   Logical records to become part of the file.
            output_chunk_size   :   Size of the buffers accumulating file bytes before file write action is called.
        """

        if not self._sul_written:
            raise RuntimeError("Storage Unit Label absent from the file; "
                               "add it calling DLISWriter.write_storage_unit_label")

        # prepare BufferedOutput object - temporarily keep added bytes, store them in the file when buffer is full
        output_chunk_size = output_chunk_size or 2 ** 32
        self._check_output_chunk_size(output_chunk_size)
        logger.debug(f"Output file will be produced in chunks of max size {output_chunk_size} bytes")
        output = BufferedOutput(int(output_chunk_size), self._byte_writer)

        # max allowed size of an LR segment body; 4 bytes reserved for VR header and another 4 for LR segment header
        max_lr_segment_size = self._visible_record_length - 8

        # loop through the logical records, transform them and write them to the file
        logger.info("Creating & writing visible records of the DLIS...")
        for lr in progressbar(logical_records, max_value=len(logical_records)):
            # represent a logical record as bytes; split it segments as needed
            for segment, segment_size in lr.represent_as_bytes().make_segments(max_lr_segment_size):
                # wrap each segment's bytes in a separate visible record and write the VR to the file
                output.add_bytes(self._make_visible_record(segment, segment_size))
        output.pass_bytes_to_writer()  # pass the remaining bytes kept in the output buffer (not full atm) to the writer

        # summarise
        logger.info(f'{len(logical_records)} written to DLIS file at {Path(self._byte_writer.filename).resolve()}')
        logger.info(f"Total file size is {self._byte_writer.total_size} bytes")
