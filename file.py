import io
from logical_record.utils.common import write_struct
from logical_record.utils.enums import RepresentationCode
import logging
from functools import lru_cache

FORMAT = '[%(levelname)s] %(asctime)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


class DLISFile(object):
    """Top level object that creates DLIS file from given list of logical record segment bodies

    Attributes:
        file_path: Absolute or relative path of output DLIS file
        storage_unit_label: A logical_record.storage_unit_label.StorageUnitLabel instance
        file_header: A logical_record.file_header.FileHeader instance
        origin: A logical_record.origin.Origin instance
        logical_records: List containing ALL logical record segments in the DLIS file
        visible_records: List of visible records that are created on the fly
        visible_record_length: Maximum length of each visible record

    .._RP66 V1 Maximum Visible Record Length:
        http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_5
    """

    def __init__(self, file_path: str, storage_unit_label, file_header,
                 origin, visible_record_length: int = None):
        """Initiates the object with given parameters"""
        self.pos = {}
        self.file_path = file_path
        self.storage_unit_label = storage_unit_label
        self.file_header = file_header
        self.origin = origin
        self.visible_records = []

        if visible_record_length:
            self.visible_record_length = visible_record_length
        else:
            self.visible_record_length = 8192

    @lru_cache
    def visible_record_bytes(self, length: int) -> bytes:
        """Create Visible Record object as bytes
        
        Args:
            length: Length of the visible record

        Returns:
            Visible Record object bytes

        """
        return write_struct(RepresentationCode.UNORM, length) \
               + write_struct(RepresentationCode.USHORT, 255) \
               + write_struct(RepresentationCode.USHORT, 1)

    def validate(self):
        """Validates the object according to RP66 V1 rules"""
        logger.info('Validating... ')
        if not self.origin.file_set_number.value:
            raise Exception('Origin object MUST have a file_set_number')

        assert self.visible_record_length >= 20, 'Minimum visible record length is 20 bytes'
        assert self.visible_record_length <= 16384, 'Maximum visible record length is 16384 bytes'
        assert self.visible_record_length % 2 == 0, 'Visible record length must be an even number'

    def assign_origin_reference(self, logical_records):
        """Assigns origin_reference attribute to self.origin.file_set_number for all Logical Records"""
        logger.info('Assigning...')

        val = self.origin.file_set_number.value
        logger.debug(f"File set number is {val}")

        self.file_header.origin_reference = val
        self.origin.origin_reference = val
        for logical_record in logical_records:
            logical_record.origin_reference = val

            if hasattr(logical_record, 'is_dictionary_controlled') \
                    and logical_record.dictionary_controlled_objects is not None:
                for obj in logical_record.dictionary_controlled_objects:
                    obj.origin_reference = val

    def raw_bytes(self, logical_records):
        """Writes bytes of entire file without Visible Record objects and splits"""
        logger.info('Writing raw bytes...')

        _stream = io.BytesIO()
        _stream.write(self.storage_unit_label.as_bytes)
        for lr in [self.file_header, self.origin] + logical_records:
            _position = _stream.tell()
            self.pos[lr] = _position
            _stream.write(lr.as_bytes)

        _bytes = _stream.getvalue()
        _stream.close()

        self.raw = bytearray(_bytes)

    def create_visible_record_dictionary(self, logical_records):
        """Creates a dictionary that guides in which positions Visible Records must be added and which
        Logical Record Segments must be split

        Returns:
            A dict object containing Visible Record split positions and related information

        """

        all_lrs = [self.file_header, self.origin] + logical_records

        q = {}

        _vr_length = 4
        _number_of_vr = 1
        _idx = 0
        vr_offset = 0
        number_of_splits = 0

        while True:

            vr_position = (self.visible_record_length * (_number_of_vr - 1)) + 80  # DON'T TOUCH THIS
            vr_position += vr_offset
            if _idx == len(all_lrs):
                q[vr_position] = {
                    'length': _vr_length,
                    'split': None,
                    'number_of_prior_splits': number_of_splits,
                    'number_of_prior_vr': _number_of_vr
                }
                break

            lrs = all_lrs[_idx]

            _lrs_position = self.get_lrs_position(lrs, _number_of_vr, number_of_splits)

            # NO NEED TO SPLIT KEEP ON
            if (_vr_length + lrs.size) <= self.visible_record_length:
                _vr_length += lrs.size
                _idx += 1

            # NO NEED TO SPLIT JUST DON'T ADD THE LAST LR
            elif vr_position + self.visible_record_length - _lrs_position < 16:
                q[vr_position] = {
                    'length': _vr_length,
                    'split': None,
                    'number_of_prior_splits': number_of_splits,
                    'number_of_prior_vr': _number_of_vr
                }

                _vr_length = 4
                _number_of_vr += 1
                vr_offset -= (vr_position + self.visible_record_length - _lrs_position)

            else:
                q[vr_position] = {
                    'length': self.visible_record_length,
                    'split': lrs,
                    'number_of_prior_splits': number_of_splits,
                    'number_of_prior_vr': _number_of_vr
                }

                _vr_length = 4 + 4 + lrs.size - (vr_position + self.visible_record_length - _lrs_position)
                _number_of_vr += 1
                _idx += 1
                number_of_splits += 1

        return q

    def add_visible_records(self, logical_records):
        """Adds visible record bytes and undertakes split operations with the guidance of vr_dict
        received from self.create_visible_record_dictionary()

        """
        logger.info('Adding visible records...')
        splits = 0

        vr_dict = self.create_visible_record_dictionary(logical_records)
        logger.info('visible record dictionary created')

        for vr_position, val in vr_dict.items():

            vr_length = val['length']
            lrs_to_split = val['split']
            number_of_prior_splits = val['number_of_prior_splits']
            number_of_prior_vr = val['number_of_prior_vr']

            self.insert_visible_record_bytes(vr_length, vr_position)

            if lrs_to_split:
                splits += 1
                # FIRST PART OF THE SPLIT
                updated_lrs_position = self.pos[lrs_to_split] \
                                       + (number_of_prior_splits * 4) \
                                       + (number_of_prior_vr * 4)

                first_segment_length = vr_position + vr_length - updated_lrs_position
                header_bytes_to_replace = lrs_to_split.split(
                    is_first=True,
                    is_last=False,
                    segment_length=first_segment_length,
                    add_extra_padding=False
                )

                self.insert_header_bytes_into_raw(header_bytes_to_replace, updated_lrs_position)

                # SECOND PART OF THE SPLIT
                second_lrs_position = vr_position + vr_length + 4
                second_segment_length = lrs_to_split.size - first_segment_length + 4
                header_bytes_to_insert = lrs_to_split.split(
                    is_first=False,
                    is_last=True,
                    segment_length=second_segment_length,
                    add_extra_padding=False
                )

                self.insert_header_bytes_into_raw_2(header_bytes_to_insert, second_lrs_position)

        logger.info(f'{splits} splits created.')

    def insert_visible_record_bytes(self, vr_length, vr_position):
        # Inserting Visible Record Bytes to the specified position
        self.raw = self.raw[:vr_position] + self.visible_record_bytes(vr_length) + self.raw[vr_position:]

    def insert_header_bytes_into_raw_2(self, header_bytes_to_insert, second_lrs_position):
        # INSERTING the header bytes of the second split part of the Logical Record Segment
        self.raw = self.raw[:second_lrs_position - 4] + header_bytes_to_insert + self.raw[second_lrs_position - 4:]

    def insert_header_bytes_into_raw(self, header_bytes_to_replace, updated_lrs_position):
        # Replacing the header bytes of the first split part of the Logical Record Segment
        self.raw = self.raw[:updated_lrs_position] + header_bytes_to_replace + self.raw[updated_lrs_position + 4:]

    def get_lrs_position(self, lrs, number_of_vr: int, number_of_splits: int):
        """Recalculates the Logical Record Segment's position

        Args:
            lrs: A logical_record.utils.core.EFLR or logical_record.utils.core.IFLR instance
            number_of_vr: Number of visible records created prior to lrs' position
            number_of_splits: Number of splits occured prior to lrs' position

        Returns:
            Recalculated position of the Logical Record Segment in the entire file

        """
        return self.pos[lrs] + (number_of_vr * 4) + (number_of_splits * 4)

    def write_to_file(self):
        """Writes the bytes to a DLIS file"""
        logger.info('Writing to file...')

        with open(self.file_path, 'wb') as f:
            f.write(self.raw)

    def write_dlis(self, logical_records):
        """Top level method that calls all the other methods to create and write DLIS bytes"""
        self.validate()
        self.assign_origin_reference(logical_records)
        self.raw_bytes(logical_records)
        self.add_visible_records(logical_records)
        self.write_to_file()
        logger.info('Done.')
