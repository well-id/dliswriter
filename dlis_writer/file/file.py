import os
import logging
from line_profiler_pycharm import profile
from progressbar import ProgressBar  # package name is progressbar2 (added to requirements)
from typing import Union

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.collections.logical_record_collection import LogicalRecordCollection
from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.logical_record.core.logical_record_bytes import LogicalRecordBytes


logger = logging.getLogger(__name__)


class DLISFile:
    """Top level object that creates DLIS file from given list of logical record segment bodies

    Attributes:
        storage_unit_label: A logical_record.storage_unit_label.StorageUnitLabel instance
        file_header: A logical_record.file_header.FileHeader instance
        origin: A logical_record.origin.Origin instance
        visible_record_length: Maximum length of each visible record

    .._RP66 V1 Maximum Visible Record Length:
        http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_5
    """

    def __init__(self, visible_record_length: int = 8192):
        """Initiates the object with given parameters"""

        self.check_visible_record_length(visible_record_length)
        self.visible_record_length = visible_record_length

        # format version is a required part of each visible record and is fixed for a given version of the standard
        self._format_version = write_struct(RepresentationCode.USHORT, 255) + write_struct(RepresentationCode.USHORT, 1)

    @staticmethod
    def check_visible_record_length(vrl):
        if vrl < 20:
            raise ValueError("Visible record length must be at least 20 bytes")

        if vrl > 16384:
            raise ValueError("Visible record length cannot be larger than 16384 bytes")

        if vrl % 2:
            raise ValueError("Visible record length must be an even number")

    @staticmethod
    def assign_origin_reference(logical_records: LogicalRecordCollection):
        """Assigns origin_reference attribute to self.origin.file_set_number for all Logical Records"""

        val = logical_records.origin.first_object.file_set_number.value

        if not val:
            raise Exception('Origin object MUST have a file_set_number')

        logger.info(f"Assigning origin reference: {val} to all logical records")
        logical_records.set_origin_reference(val)

    def make_bytes_of_logical_records(self, logical_records: LogicalRecordCollection):
        """Writes bytes of entire file without Visible Record objects and splits"""

        for lr in logical_records:
            if isinstance(lr, MultiFrameData):
                for frame_data in lr:
                    yield frame_data.represent_as_bytes()
            else:
                yield lr.represent_as_bytes()

    def _make_visible_record(self, body, size=None) -> bytes:

        if size is None:
            size = len(body)

        size += 4

        if size > self.visible_record_length:
            raise ValueError(f"VR length is too large; got {size}, max is {self.visible_record_length}")

        return RepresentationCode.UNORM.converter.pack(size) + self._format_version + body

    @profile
    def create_visible_records(self, n_records, all_lrb_iter, writer, chunk_size=2**32):
        """Adds visible record bytes and undertakes split operations with the guidance of vr_dict
        received from self.create_visible_record_dictionary()

        """

        hs = 4  # header size (both for logical record segment and visible record)
        mbs = 12  # minimum logical record body size (min LRS size is 16 incl. 4-byte header)

        bar = ProgressBar(max_value=n_records)

        output = bytearray(chunk_size)
        sul_bytes = next(all_lrb_iter).bytes
        total_filled_output_len = len(sul_bytes)
        current_filled_output_len = total_filled_output_len
        output[:current_filled_output_len] = sul_bytes  # SUL - add as-is, don't wrap in a visible record
        first_output_chunk = True

        current_vr_body = b''
        current_vr_body_size = 0
        max_vr_body_size = self.visible_record_length - hs
        position_in_current_lrb = 0

        lrb: LogicalRecordBytes = None
        i = 0
        remaining_lrb_size = 0
        vr_space = max_vr_body_size - hs

        def next_vr():
            nonlocal output, current_vr_body, total_filled_output_len, current_filled_output_len, first_output_chunk
            added_len = current_vr_body_size + hs
            new_len = current_filled_output_len + added_len
            while new_len > chunk_size:
                writer(output[:current_filled_output_len], append=not first_output_chunk)
                first_output_chunk = False
                output = bytearray(chunk_size)
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
                lrb = next(all_lrb_iter)
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

    def write_dlis(self, logical_records: LogicalRecordCollection, filename: Union[str, bytes, os.PathLike]):
        """Top level method that calls all the other methods to create and write DLIS bytes"""

        logical_records.check_objects()

        def file_writer(bts, append=False):
            self.write_bytes_to_file(bts, filename, append=append)

        self.assign_origin_reference(logical_records)
        all_lrb_iter = self.make_bytes_of_logical_records(logical_records)
        self.create_visible_records(len(logical_records), all_lrb_iter, writer=file_writer)
        logger.info(f'DLIS file created at {filename}')
    