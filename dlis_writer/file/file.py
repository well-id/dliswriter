import os
import numpy as np
import logging
from functools import lru_cache
from itertools import chain
from collections import namedtuple
from line_profiler_pycharm import profile
from progressbar import progressbar  # package name is progressbar2 (added to requirements)
from typing import Union, Dict

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.file.frame_data_capsule import FrameDataCapsule


logger = logging.getLogger(__name__)


def log_progress(message):
    """Wrap a function, so that log messages are displayed: a custom message at the start and 'Done' at the end."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(message)
            result = func(*args, **kwargs)
            logger.debug("Done")
            return result
        return wrapper
    return decorator


VRFields = namedtuple('VRFields', field_names=('length', 'split', 'number_of_prior_splits', 'number_of_prior_vr'))


class PositionedArray:
    def __init__(self, n):
        self._bytes = np.zeros(n, dtype=np.uint8)
        self._mask = np.zeros(n, dtype=bool)
        self._max_pos = self._bytes.size

    @property
    def bytes(self):
        return self._bytes

    @property
    def mask(self):
        return self._mask

    def insert_items(self, pos: int, items: bytes):
        n = len(items)
        if pos + n > self._max_pos:
            raise RuntimeError("No more space in the array")

        if self._mask[pos]:
            # shift the bytes already at the requested position to the right by 4 indices
            # (assumed length of the inserted bytes is always 4, and otherwise the arrays are filled with zeros)
            self._mask[pos + 4:pos + 8] = self._mask[pos:pos + 4]
            self._bytes[pos + 4:pos + 8] = self._bytes[pos:pos + 4]

        # insert the new bytes at the requested positions and mark these positions in the mask array
        self.mask[pos:pos + 4] = True
        self._bytes[pos:pos + 4] = np.frombuffer(items, dtype=np.uint8)


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

    def __init__(self, storage_unit_label, file_header, origin, visible_record_length: int = None):
        """Initiates the object with given parameters"""
        self.pos = {}
        self.storage_unit_label = storage_unit_label
        self.file_header = file_header
        self.origin = origin

        self.visible_record_length = visible_record_length if visible_record_length else 8192
        self._vr_struct = write_struct(RepresentationCode.USHORT, 255) + write_struct(RepresentationCode.USHORT, 1)

    @lru_cache
    def create_visible_record_as_bytes(self, length: int) -> bytes:
        """Create Visible Record object as bytes
        
        Args:
            length: Length of the visible record

        Returns:
            Visible Record object bytes

        """

        return write_struct(RepresentationCode.UNORM, length) + self._vr_struct

    @log_progress("Validating...")
    def validate(self):
        """Validates the object according to RP66 V1 rules"""

        if not self.origin.file_set_number.value:
            raise Exception('Origin object MUST have a file_set_number')

        assert self.visible_record_length >= 20, 'Minimum visible record length is 20 bytes'
        assert self.visible_record_length <= 16384, 'Maximum visible record length is 16384 bytes'
        assert self.visible_record_length % 2 == 0, 'Visible record length must be an even number'

    @log_progress("Assigning origin reference")
    def assign_origin_reference(self, data_capsule: FrameDataCapsule):
        """Assigns origin_reference attribute to self.origin.file_set_number for all Logical Records"""

        val = self.origin.file_set_number.value
        logger.debug(f"File set number is {val}")

        self.file_header.origin_reference = val
        self.origin.origin_reference = val
        for logical_record in progressbar(data_capsule):
            logical_record.origin_reference = val

            if hasattr(logical_record, 'is_dictionary_controlled') \
                    and logical_record.dictionary_controlled_objects is not None:
                for obj in logical_record.dictionary_controlled_objects:
                    obj.origin_reference = val

    @log_progress("Writing raw bytes...")
    def create_raw_bytes(self, data_capsule: FrameDataCapsule) -> np.ndarray:
        """Writes bytes of entire file without Visible Record objects and splits"""

        all_records = chain((self.storage_unit_label, self.file_header, self.origin), data_capsule)

        n = 3 + len(data_capsule)
        all_records_bytes = [None] * n
        all_positions = [0] + [None] * n
        current_pos = 0
        for i, lr in progressbar(enumerate(all_records), max_value=n):
            b = lr.represent_as_bytes()  # grows with data size more than row number
            all_records_bytes[i] = b
            current_pos += b.size
            all_positions[i+1] = current_pos
            self.pos[lr.key] = all_positions[i]

        raw_bytes = np.zeros(int(all_positions[-1]*2.0), dtype=np.uint8)  # avoid integer overflow :)

        for i in range(n):
            raw_bytes[all_positions[i]:all_positions[i+1]] = all_records_bytes[i]

        return raw_bytes

    @log_progress("Creating visible record dictionary...")
    def create_visible_record_dictionary(self, data_capsule: FrameDataCapsule) -> Dict[int, VRFields]:
        """Creates a dictionary that guides in which positions Visible Records must be added and which
        Logical Record Segments must be split

        Returns:
            A dict object containing Visible Record split positions and related information

        """

        all_records = chain((self.file_header, self.origin), data_capsule)
        n = 2 + len(data_capsule)

        visible_record_length = self.visible_record_length

        q = {}          # dictionary to contain all visible records information

        vr_length = 4
        n_vrs = 1       #: number of visible records
        vr_offset = 0
        n_splits = 0    #: number of created splits
        vr_position = 0

        def process_iteration(_lrs):
            nonlocal vr_position, vr_length, vr_offset, n_vrs, n_splits

            vr_position = (visible_record_length * (n_vrs - 1)) + 80  # DON'T TOUCH THIS
            vr_position += vr_offset
            _lrs_size = _lrs.size
            _lrs_position = self.pos[lrs.key] + 4 * (n_vrs + n_splits)
            _position_diff = vr_position + visible_record_length - _lrs_position  # idk how to call this, but it's reused

            # option A: NO NEED TO SPLIT KEEP ON
            if (vr_length + _lrs_size) <= visible_record_length:
                vr_length += _lrs_size

            # option B: NO NEED TO SPLIT JUST DON'T ADD THE LAST LR
            elif _position_diff < 16:
                q[vr_position] = VRFields(vr_length, None, n_splits, n_vrs)
                vr_length = 4
                n_vrs += 1
                vr_offset -= _position_diff
                process_iteration(_lrs)  # need to do A, B, or C for the same lrs again

            # option C
            else:
                q[vr_position] = VRFields(visible_record_length, _lrs, n_splits, n_vrs)
                vr_length = 8 + _lrs_size - _position_diff
                n_vrs += 1
                n_splits += 1

        # note: this is a for-loop, but with a recursive element inside
        # some lrs-es need to be processed multiple times (see option B in process_iteration)
        for lrs in progressbar(all_records, max_value=n):
            process_iteration(lrs)

        # last vr
        q[vr_position] = VRFields(vr_length, None, n_splits, n_vrs)

        return q

    @log_progress("Adding visible records...")
    @profile
    def add_visible_records(self, vr_dict: dict, raw_bytes: np.ndarray) -> np.ndarray:
        """Adds visible record bytes and undertakes split operations with the guidance of vr_dict
        received from self.create_visible_record_dictionary()

        """

        # added bytes: 4 bytes per visible record and 4 per header  # TODO: is it always 4?
        total_vr_length = 4 * len(vr_dict)  # bytes added due to inserting visible record bytes (first part of the loop)
        splits = sum(int(bool(val.split)) for val in vr_dict.values())  # how many splits are done (not for all vr's)
        total_header_length = 4 * splits  # bytes added due to inserting 'header bytes' (see 'second part of the split')

        # expected total length of the raw_bytes array after the vr and header bytes are inserted
        total_len = raw_bytes.size + total_vr_length + total_header_length

        # New approach: instead of inserting the bytes (changing the length of the raw_bytes at every iteration),
        # prepare arrays which will only hold the inserted bytes already at the correct positions;
        # otherwise, these arrays are filled with zeros.
        # Also keep 'mask' arrays, marking the positions at which the 'inserted' bytes are placed.
        # When the loop is finished, re-map the original raw_bytes onto the non-occupied positions in the new array.
        # Note: there are actually two types of operations done here (as it was in the original code): inserting
        # and replacing bytes. In the loop, first, a visible record is *inserted*, then (if a split is done)
        # header bytes are *replaced* (see 'first part of the split'), and finally more bytes are *inserted*
        # (see 'second part of the split'). To preserve the correct positions of the bytes, bytes coming from the two
        # types of operations are kept in two separate arrays (with corresponding masks): bytes_inserted
        # and bytes_replaced.
        bytes_inserted = PositionedArray(total_len)
        bytes_replaced = PositionedArray(total_len)

        for vr_position, val in progressbar(vr_dict.items()):

            vr_length = val.length

            # 'inserting' visible record bytes (changed array length in the original code)
            self.insert_bytes(
                bytes_inserted,
                bytes_to_insert=self.create_visible_record_as_bytes(vr_length),
                position=vr_position
            )

            if lrs_to_split := val.split:
                # FIRST PART OF THE SPLIT
                pos_shift = 4 * (val.number_of_prior_vr + val.number_of_prior_splits)
                updated_lrs_position = self.pos[lrs_to_split.key] + pos_shift

                first_segment_length = vr_position + vr_length - updated_lrs_position
                header_bytes_to_replace = lrs_to_split.split(
                    is_first=True,
                    is_last=False,
                    segment_length=first_segment_length,
                    add_extra_padding=False
                )

                # replacing header bytes (no change in the array length in the original code)
                self.insert_bytes(
                    bytes_replaced,
                    bytes_to_insert=header_bytes_to_replace,
                    position=updated_lrs_position
                )

                # SECOND PART OF THE SPLIT
                second_lrs_position = vr_position + vr_length + 4
                second_segment_length = lrs_to_split.size - first_segment_length + 4
                header_bytes_to_insert = lrs_to_split.split(
                    is_first=False,
                    is_last=True,
                    segment_length=second_segment_length,
                    add_extra_padding=False
                )

                # 'inserting' header bytes (changed array length in the original code)
                self.insert_bytes(
                    bytes_inserted,
                    bytes_to_insert=header_bytes_to_insert,
                    position=second_lrs_position - 4
                )

        logger.debug(f"{splits} splits created")

        # use the bytes_inserted as the destination array
        # map the original raw_bytes on the unoccupied positions in bytes_inserted
        # first check that the empty bytes counts are correct
        if (unoccupied_length := (total_len - bytes_inserted.mask.sum())) != raw_bytes.size:
            raise RuntimeError("Error in inserting visible record bytes: the number of unoccupied bytes in the array "
                               f"{unoccupied_length} does not match the number of the raw bytes {raw_bytes.size})")
        bytes_inserted.bytes[~bytes_inserted.mask] = raw_bytes

        # apply the replaced header bytes
        bytes_inserted.bytes[bytes_replaced.mask] = bytes_replaced.bytes[bytes_replaced.mask]

        return bytes_inserted.bytes  # this is the array containing all the bytes combined now

    @staticmethod
    def check_length(bytes_to_check: bytes, expected_length: int = 4) -> None:
        """Check that the length of bytes to be inserted/replaced matches the expected length.

        Args:
            bytes_to_check:     The bytes to be inserted/replaced.
            expected_length:    Expected number of bytes.

        Raises:
            ValueError if the actual length of the bytes does not match the expected one.


        Note:
            The performance-upgrade modifications are based on the assumptions that the number of inserted/replaced
            bytes is always 4. This method has been put in place to make it easier to catch and understand the error
            on the off chance the aforementioned assumption is not always valid.
        """

        if (nb := len(bytes_to_check)) != expected_length:
            raise ValueError(f"Expected {expected_length} bytes, got {nb}")

    def insert_bytes(self, array_of_bytes: PositionedArray, bytes_to_insert: bytes, position: int) -> None:
        """Insert (or replace) bytes at the given position in the byte array.

        Additionally, mark the positions at which the bytes were put in the corresponding mask array.

        Args:
            array_of_bytes:     Array into which the bytes should be inserted and the corresponding mask.
            bytes_to_insert:    Bytes that will be inserted into the array.
            position:           Position in the array_of_bytes (index) at which the first of the bytes will be placed.

        Note:
            In the original code, bytes were frequently inserted twice into the same position. This resulted in
            shifting the earlier inserted bytes by 4 indices to the right (while the array length changed).
            In this implementation, the length of the array is constant and the shifting is achieved by manually moving
            the 4 bytes already present at the given position to the right by 4 indices. This is done both in the
            array of bytes and the mask array, and only if the mask value at the concerned position is already True
            at the entry to the method.
        """

        self.check_length(bytes_to_insert)  # the code below is based on the assumption that we *always* insert 4 bytes

        array_of_bytes.insert_items(pos=position, items=bytes_to_insert)
        # operations done in-place - no return value

    @staticmethod
    @log_progress("Writing to file...")
    def write_bytes_to_file(raw_bytes: bytes, filename: Union[str, bytes, os.PathLike]):
        """Writes the bytes to a DLIS file"""

        with open(filename, 'wb') as f:
            f.write(raw_bytes)

        logger.info(f"Data written to file: '{filename}'")

    @profile
    def write_dlis(self, data_capsule: FrameDataCapsule, filename: Union[str, bytes, os.PathLike]):
        """Top level method that calls all the other methods to create and write DLIS bytes"""

        self.validate()
        self.assign_origin_reference(data_capsule)
        raw_bytes = self.create_raw_bytes(data_capsule)
        vr_dict = self.create_visible_record_dictionary(data_capsule)
        all_bytes = self.add_visible_records(vr_dict, raw_bytes)
        self.write_bytes_to_file(all_bytes.tobytes(), filename)
        logger.info('DLIS file created.')
