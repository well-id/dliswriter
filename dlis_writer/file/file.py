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

    def _create_visible_records(self, logical_records: FileLogicalRecords, writer: callable, output_chunk_size=2 ** 32):
        """Create visible records constituting the DLIS file.

        Bytes of each logical record are placed in a new visible record. If necessary, bytes of logical record are split
        across several visible records.
        The file is created in chunks. Consecutive visible records are added to a chunk until it reaches its maximum
        size (defined by the output_chunk_size argument). The chunk is then saved to the file and a new output chunk
        is created.

        Args:
            logical_records     :   FileLogicalRecords object containing logical records to be put in the DLIS file.
            writer              :   Function taking care of storing output chunks into the file.
            output_chunk_size   :   Size (in bytes) of chunks in which the output file will be created.
        """

        all_lrb_gen = self._make_lr_bytes_generator(logical_records)  # generator yielding bytes of the logical records
        n_records = len(logical_records)  # total number of logical records (including Storage Unit Label)

        hs = 4  # header size (both for logical record segment and visible record)
        mbs = 12  # minimum logical record body size (min LRS size is 16 incl. 4-byte header)

        bar = ProgressBar(max_value=n_records)

        logger.debug(f"Output file will be produced in chunks of max size {output_chunk_size} bytes")

        output = bytearray(output_chunk_size)   # pre-allocate space for the first output chunk
        sul_bytes = next(all_lrb_gen).bytes     # create bytes of the Storage Unit Label (first logical record)
        total_filled_output_len = len(sul_bytes)    # total number of bytes added to the file
        current_filled_output_len = total_filled_output_len  # number of bytes added to the current output chunk
        output[:current_filled_output_len] = sul_bytes  # add the SUL bytes - add as-is, don't wrap in a visible record
        first_output_chunk = True  # mark that this is the first output chunk - writing will be in 'w', not 'a' mode

        current_vr_body = b''  # body of the current visible record
        current_vr_body_size = 0  # size of the current visible record
        max_vr_body_size = self.visible_record_length - hs  # maximal allowed size of a VR body (before adding header)
        position_in_current_lrb = 0  # how many bytes of the current logical record have been processed

        lrb: LogicalRecordBytes = None  # bytes of the current logical record
        i = 0  # iteration number (for the progress bar) - how many logical records have been processed
        remaining_lrb_size = 0  # how many bytes still remain in the current logical record (used if the LR is split)
        vr_space = max_vr_body_size - hs  # how much space still remains in the current visible record

        def next_vr():
            nonlocal output, current_vr_body, total_filled_output_len, current_filled_output_len, first_output_chunk
            added_len = current_vr_body_size + hs
            new_len = current_filled_output_len + added_len
            while new_len > output_chunk_size:
                writer(output[:current_filled_output_len], append=not first_output_chunk)
                first_output_chunk = False
                output = bytearray(output_chunk_size)
                current_filled_output_len = 0
                new_len = added_len
                logger.debug(f"Making new output chunk; current total output size is {total_filled_output_len}")
            output[current_filled_output_len:new_len] = self._make_visible_record(current_vr_body, size=current_vr_body_size)
            total_filled_output_len += added_len
            current_filled_output_len += added_len
            current_vr_body = b''

        def next_lrb():
            nonlocal lrb, i, position_in_current_lrb, remaining_lrb_size
            try:
                lrb = next(all_lrb_gen)
            except StopIteration:
                return False
            else:
                bar.update(i)
                i += 1
                position_in_current_lrb = 0
                remaining_lrb_size = lrb.size  # position in current lrb is 0
                next_vr()
            return True

        logger.info("Creating visible records of the DLIS...")

        next_lrb()

        while True:
            if not remaining_lrb_size:
                if not next_lrb():
                    break

            if remaining_lrb_size <= vr_space:
                current_vr_body += lrb.make_segment(start_pos=position_in_current_lrb)
                # VR body size: header (4 bytes), length of the added lrb tail, and padding (if the former is odd)
                current_vr_body_size = hs + remaining_lrb_size + (remaining_lrb_size % 2)
                if not next_lrb():
                    break

            else:
                segment_size = min(vr_space, remaining_lrb_size)
                future_remaining_lrb_size = remaining_lrb_size - segment_size
                if future_remaining_lrb_size < mbs:
                    segment_size -= mbs - future_remaining_lrb_size
                    future_remaining_lrb_size = mbs
                if segment_size >= mbs:
                    current_vr_body += lrb.make_segment(start_pos=position_in_current_lrb, n_bytes=segment_size)
                    current_vr_body_size = segment_size + hs
                    position_in_current_lrb += segment_size
                    remaining_lrb_size = future_remaining_lrb_size
                next_vr()

        next_vr()
        bar.finish()
        writer(output[:current_filled_output_len], append=not first_output_chunk)

        logger.info(f"Final total file size is {total_filled_output_len} bytes")

    @staticmethod
    def write_bytes_to_file(raw_bytes: bytes, filename: Union[str, bytes, os.PathLike], append=False):
        """Writes the bytes to a DLIS file"""

        mode = 'ab' if append else 'wb'

        logger.debug("Writing bytes to file")
        with open(filename, mode) as f:
            f.write(raw_bytes)

    def create_dlis(self, config, data, filename: Union[str, bytes, os.PathLike], input_chunk_size=None,
                    output_chunk_size=2**32):
        """Top level method that calls all the other methods to create and write DLIS bytes"""

        logical_records = FileLogicalRecords.from_config_and_data(config, data, chunk_size=input_chunk_size)
        logical_records.check_objects()
        self._assign_origin_reference(logical_records)

        def file_writer(bts, append=False):
            self.write_bytes_to_file(bts, filename, append=append)

        self._create_visible_records(
            logical_records,
            writer=file_writer,
            output_chunk_size=output_chunk_size
        )

        logger.info(f'DLIS file created at {filename}')


    