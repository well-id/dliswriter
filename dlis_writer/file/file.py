import os
import logging
from progressbar import ProgressBar  # package name is progressbar2 (added to requirements)
from typing import Union, Optional

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.collections.file_logical_records import FileLogicalRecords
from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.logical_record.core.logical_record_bytes import LogicalRecordBytes


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

        def write_bytes(self, bts: bytes, size: Optional[int] = None):
            """Write (in 'wb' or 'ab' mode, as needed) the bytes into the file.

            Args:
                bts     :   Bytes to be written to the file.
                size    :   Number of bytes to be written. If not provided, it is calculated from bts.
            """

            mode = 'ab' if self._append else 'wb'

            logger.debug("Writing bytes to file")
            with open(self._filename, mode) as f:
                f.write(bts)

            self._append = True  # in the future calls, append bytes to the file
            self._total_size += (size or len(bts))

        def write_output_chunk(self, chunk: "DLISFile.OutputChunk"):
            self.write_bytes(chunk.filled_bytes, size=chunk.filled_size)

    class OutputChunk:
        def __init__(self, size, writer: "DLISFile.DLISFileWriter"):
            self._bts = bytearray(size)
            self._filled_size = 0
            self._total_size = size

            self._writer = writer

        @property
        def filled_size(self):
            return self._filled_size

        @property
        def filled_bytes(self):
            return self._bts[:self._filled_size]

        def add_bytes(self, bts: bytes, size: Optional[int] = None):
            size = size or len(bts)
            new_size = self._filled_size + size

            if new_size > self._total_size:
                self._writer.write_output_chunk(self)
                self.clear()
                logger.debug(f"Making new output chunk; current total output size is {self._writer.total_size}")
                new_size = size

            self._bts[self._filled_size:new_size] = bts
            self._filled_size = new_size

        def clear(self):
            self._bts = bytearray(self._total_size)
            self._filled_size = 0

    class TrackedProgressBar(ProgressBar):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._i = 0

        def update(self, *args, **kwargs):
            super().update(self._i)
            self._i += 1

    def __init__(self, visible_record_length: int = 8192):
        """Initialise DLISFile object.

        Args:
            visible_record_length   :   Maximum allowed length of visible records (physical file units) in the created
                                        file. Expressed in bytes.
        """

        self._check_visible_record_length(visible_record_length)
        self.visible_record_length: int = visible_record_length  #: Maximum allowed visible record length, in bytes

        # format version is a required part of each visible record and is fixed for a given version of the standard
        self._format_version = write_struct(RepresentationCode.USHORT, 255) + write_struct(RepresentationCode.USHORT, 1)

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

        val = logical_records.origin.first_object.file_set_number.value

        if not val:
            raise Exception('Origin object MUST have a file_set_number')

        logger.info(f"Assigning origin reference: {val} to all logical records")
        logical_records.set_origin_reference(val)

    @staticmethod
    def _make_lr_bytes_generator(logical_records: FileLogicalRecords):
        """Create a generator yielding bytes of all provided logical records."""

        for lr in logical_records:
            if isinstance(lr, MultiFrameData):
                for frame_data in lr:
                    yield frame_data.represent_as_bytes()
            else:
                yield lr.represent_as_bytes()

    def _make_visible_record(self, body: Union[bytes, bytearray], size: Optional[int] = None) -> bytes:
        """Create a visible record (physical DLIS unit) from the provided body bytes.

        Args:
            body    :   Bytes to create the visible record from.
            size    :   Number of bytes in the body. If not provided, it is calculated from the body object.

        Returns:
            Created visible record (provided body bytes preceded by header bytes) as a bytes object.
        """

        if size is None:
            size = len(body)

        size += 4  # 4 header bytes will be added

        if size > self.visible_record_length:
            raise ValueError(f"VR length is too large; got {size}, max is {self.visible_record_length}")

        return RepresentationCode.UNORM.converter.pack(size) + self._format_version + body

    def _create_visible_records(self, logical_records: FileLogicalRecords, writer: "DLISFile.DLISFileWriter",
                                output_chunk_size=2 ** 32):
        """Create visible records constituting the DLIS file.

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

        all_lrb_gen = self._make_lr_bytes_generator(logical_records)  # generator yielding bytes of the logical records

        bar = self.TrackedProgressBar(max_value=len(logical_records))

        logger.debug(f"Output file will be produced in chunks of max size {output_chunk_size} bytes")

        output_chunk = self.OutputChunk(output_chunk_size, writer)
        output_chunk.add_bytes(next(all_lrb_gen).bytes)  # add SUL bytes (don't wrap in a visible record)

        max_lr_segment_size = self.visible_record_length - 8  # max allowed size of a LR segment

        logger.info("Creating visible records of the DLIS...")

        for lrb in all_lrb_gen:
            for segment, segment_size in lrb.make_segments(max_lr_segment_size):
                output_chunk.add_bytes(self._make_visible_record(segment, segment_size))

            bar.update()

        bar.finish()
        writer.write_output_chunk(output_chunk)

        logger.info(f"Final total file size is {writer.total_size} bytes")

    def create_dlis(self, config, data, filename: Union[str, bytes, os.PathLike], input_chunk_size=None,
                    output_chunk_size=2**32):
        """Top level method that calls all the other methods to create and write DLIS bytes"""

        logical_records = FileLogicalRecords.from_config_and_data(config, data, chunk_size=input_chunk_size)
        logical_records.check_objects()
        self._assign_origin_reference(logical_records)

        self._create_visible_records(
            logical_records,
            writer=self.DLISFileWriter(filename),
            output_chunk_size=output_chunk_size
        )

        logger.info(f'DLIS file created at {filename}')


    