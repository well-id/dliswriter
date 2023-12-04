import os
import logging
from progressbar import progressbar  # package name is progressbar2 (added to requirements)
from typing import Union, Optional
from configparser import ConfigParser

from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.collections.file_logical_records import FileLogicalRecords
from dlis_writer.utils.source_data_objects import SourceDataObject


logger = logging.getLogger(__name__)


class DLISFile:
    """Create a DLIS file given data and structure information (specification of logical records)."""

    class DLISFileWriter:
        """Write bytes to DLIS file."""

        def __init__(self, filename: Union[str, bytes, os.PathLike]):
            """Initialise DLISFileWriter.

            Args:
                filename    :   Name of the file the bytes should be written to.
            """

            self._filename = filename
            self._append = False  # changes to True in first call of write_bytes
            self._total_size = 0

        @property
        def total_size(self) -> int:
            """Number of bytes which have been written into the file."""

            return self._total_size

        def write_bytes(self, bts: Union[bytes, bytearray], size: Optional[int] = None):
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

        def __init__(self, size: int, writer: "DLISFile.DLISFileWriter"):
            """Initialise BufferedOutput object.

            Args:
                size    :   Size of the buffer.
                writer  :   File writer object.
            """

            self._bts = bytearray(size)     #: the buffer
            self._filled_size = 0           #: how many bytes are in the current buffer
            self._buffer_size = size        #: size of the output buffer (needed when setting up a new one)

            self._writer = writer           #: file writer object

        def add_bytes(self, bts: Union[bytes, bytearray], size: Optional[int] = None):
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

        def pass_bytes_to_writer(self):
            """Send the currently kept bytes to the file writer. Set up a new, empty output buffer."""

            self._writer.write_bytes(self._bts[:self._filled_size], self._filled_size)

            # set up a new output buffer
            self._bts = bytearray(self._buffer_size)
            self._filled_size = 0

    def __init__(self, visible_record_length: int = 8192):
        """Initialise DLISFile object.

        Args:
            visible_record_length   :   Maximum allowed length of visible records (physical file units) in the created
                                        file. Expressed in bytes.
        """

        self._check_visible_record_length(visible_record_length)
        self._visible_record_length: int = visible_record_length  #: Maximum allowed visible record length, in bytes

        # format version is a required part of each visible record and is fixed for a given version of the standard
        self._fmt_version = RepresentationCode.USHORT.convert(255) + RepresentationCode.USHORT.convert(1)

    @staticmethod
    def _check_visible_record_length(vrl: int):
        """Check the type and value of visible record length against several criteria."""

        if not isinstance(vrl, int):
            raise TypeError(f"Visible record length must be an integer; got {type(vrl)}")

        if vrl < 20:
            raise ValueError("Visible record length must be at least 20 bytes")

        if vrl > 16384:
            raise ValueError("Visible record length cannot be larger than 16384 bytes")

        if vrl % 2:
            raise ValueError("Visible record length must be an even number")

    @staticmethod
    def _assign_origin_reference(logical_records: FileLogicalRecords):
        """Assign origin_reference attribute of all Logical Records to file set number of the Origin."""

        if logical_records.origin.first_object is None:
            raise RuntimeError("No origin defined")

        val = logical_records.origin.first_object.file_set_number.value

        if not val:
            raise Exception('Origin object MUST have a file_set_number')

        logger.info(f"Assigning origin reference: {val} to all logical records")
        logical_records.set_origin_reference(val)

    def _make_visible_record(self, body: Union[bytes, bytearray], size: Optional[int] = None) -> bytes:
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

    def _check_output_chunk_size(self, output_chunk_size: Union[int, float]):
        """Check output chunk size type (integer or float with zero decimal part) and value (>= max VR length)."""

        if not isinstance(output_chunk_size, (int, float)):
            raise TypeError(f"Output chunk size must be a number; got {type(output_chunk_size)}")

        if output_chunk_size % 1:
            raise ValueError(f"Output chunk size must be an integer; got {output_chunk_size}")

        if output_chunk_size < self._visible_record_length:
            raise ValueError(f"Output chunk size cannot be smaller than max visible record length "
                             f"(= {self._visible_record_length}); got {output_chunk_size}")

    def _create_visible_records(self, logical_records: FileLogicalRecords, writer: "DLISFile.DLISFileWriter",
                                output_chunk_size: Union[int, float] = 2 ** 32):
        """Create visible records constituting the DLIS file. Write the created bytes to the file.

        Bytes of each logical record are placed in a new visible record. If necessary, bytes of logical record are split
        across several visible records.
        The file is created in chunks. Consecutive visible records are added to a chunk until it reaches its maximum
        size (defined by the output_chunk_size argument). The chunk is then saved to the file and a new output chunk
        is created.

        Args:
            logical_records     :   FileLogicalRecords object containing logical records to be put in the DLIS file.
            writer              :   DLISFileWriter object, taking care of writing output chunks into the file.
            output_chunk_size   :   Size (in bytes) of chunks in which the output file will be created.
        """

        all_lrb_gen = (lr.represent_as_bytes() for lr in logical_records)  # generator yielding logical records' bytes

        # prepare BufferedOutput object - temporarily keep added bytes, store them in the file when buffer is full
        self._check_output_chunk_size(output_chunk_size)
        logger.debug(f"Output file will be produced in chunks of max size {output_chunk_size} bytes")
        output = self.BufferedOutput(int(output_chunk_size), writer)

        output.add_bytes(next(all_lrb_gen).bts)  # add SUL bytes (don't wrap in a visible record)

        max_lr_segment_size = self._visible_record_length - 8  # max allowed size of an LR segment body
        # ^ 4 bytes reserved for VR header and another 4 for LR segment header

        logger.info("Creating visible records of the DLIS...")
        for lrb in progressbar(all_lrb_gen, max_value=len(logical_records)-1):  # len(...)-1 because SUL already added
            for segment, segment_size in lrb.make_segments(max_lr_segment_size):  # split LRs to segments as needed
                output.add_bytes(self._make_visible_record(segment, segment_size))  # each segment in a separate VR
        output.pass_bytes_to_writer()  # pass the remaining bytes kept in the output buffer (not full atm) to the writer

        logger.info(f"Final total file size is {writer.total_size} bytes")

    def create_dlis(self, config: ConfigParser, data: SourceDataObject, filename: Union[str, os.PathLike[str]],
                    input_chunk_size: Optional[int] = None, output_chunk_size: Union[int, float] = 2**32):
        """Create a DLIS file from logical records specification (found in the config) and numerical data.

        Args:
            config              :   Object with information needed to create all logical records of the file.
            data                :   Object wrapping the curves and images data of the file.
            filename            :   Name of the file to be created. Note: at this point, no file name / directory checks
                                    (file already exists / directory write access / etc.) are performed.
            input_chunk_size    :   Size of the chunks (in rows) in which input data will be loaded to be processed.
            output_chunk_size   :   Size of the buffers accumulating file bytes before file write action is called.
        """

        # create all logical records (or generators of these) from the config and data
        logical_records = FileLogicalRecords.from_config_and_data(config, data, chunk_size=input_chunk_size)
        logical_records.check_objects()  # check that all required objects are there

        self._assign_origin_reference(logical_records)

        # this is the bit where the file is actually created
        self._create_visible_records(
            logical_records,
            writer=self.DLISFileWriter(filename),
            output_chunk_size=output_chunk_size
        )

        logger.info(f'DLIS file created at {filename}')


    