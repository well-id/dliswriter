from common.data_types import struct_type_dict
from common.data_types import write_struct

from utils.converters import get_ascii_bytes

from component import Set

class LogicalRecordSegment(object):

    def __init__(self,
                 segment_length:int=None, # Will be calculated after the segment is created
                 logical_record_type:int=None,
                 is_eflr:bool=True,
                 has_predecessor_segment:bool=False,
                 has_successor_segment:bool=False,
                 is_encrypted:bool=False,
                 has_encryption_protocol:bool=False,
                 has_checksum:bool=False,
                 has_trailing_length:bool=False,
                 has_padding:bool=False,
                 set_component:object=None):


        '''  


        :segment_length --> Integer. Denotes the length of logical record segment in bytes.
        
        :logical_record_type --> Integer denoting the Logical Record Type (to be converted to USHORT). 
        For all record types please see: http://w3.energistics.org/rp66/v1/rp66v1_appa.html#A_2
        For example, logical_record_type=0 will be type FHLR, which is "File Header"
        

        ATTRIBUTES
        
        All 8 arguments listed below must be provided with a value of either True or False.

        :is_eflr --> Abbreviation for "Explicitly Formatted Logical Record"
        :has_predecessor_segment
        :has_successor_segment
        :is_encrypted
        :has_encryption_protocol
        :has_checksum
        :has_trailing_length
        :has_padding
        
        To write these attributes, all 8 bits will be merged. Let's say is_eflr="1" and remaining 7 attributes="0".
        These attributes will be merged into a string "10000000" then we will get the int('10000000',2) and convert it to USHORT
        and append to DLIS file.

        RP66 V1 Section 3.2.3.2 Comment Number 2 (Under sub-header "Comments") explains this part:

            QUOTE
            2. The Logical Record Segment Attribute bits for Segment 
                    #1 indicate an EFLR structure (bit 1),
                    no predecessor segment (bit 2),
                    a successor segment (bit 3),
                    no encryption (bit 4),
                    no Encryption Packet (bit 5),
                    a checksum (bit 6),
                    a Trailing Length (bit 7),
                    and no Padding (bit 8)
            END QUOTE FROM --> http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_3_2

        This table also displays Logical Record Segment Attributes --> http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1


        First 2 bytes specify the "Logical Record Segment Length" and data type is UNORM
        Next 1 byte is an integer (type USHORT) and 



        :set_component -> Every logical record segment must have a set component.


        References:
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec3.html
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec5.html#5_1
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_3_2
            -> https://github.com/Teradata/dlispy/blob/b2d682dbfd8a6f7d0074351b603e22f97524fee6/dlispy/LogicalRecordSegment.py
        
        '''


        self.segment_length = segment_length
        self.logical_record_type = logical_record_type

        # Attributes
        self.is_eflr = str(int(is_eflr))
        self.has_predecessor_segment = str(int(has_predecessor_segment))
        self.has_successor_segment = str(int(has_successor_segment))
        self.is_encrypted = str(int(is_encrypted))
        self.has_encryption_protocol = str(int(has_encryption_protocol))
        self.has_checksum = str(int(has_checksum))
        self.has_trailing_length = str(int(has_trailing_length))
        self.has_padding = str(int(has_padding))

        # Set component
        self.set_component = set_component

        # Template
        self.template = None

        # Objects
        self.objects = []



    def get_as_bytes(self):



        # Constructing the body bytes first as we need to provide the lenght of the segment in the header.

        _body_bytes = b''

        # BODY
        if self.set_component:
            _body_bytes += self.set_component.get_as_bytes()

        if self.template:
            _body_bytes += self.template.get_as_bytes()

        for _object in self.objects:
            _body_bytes += _object.get_as_bytes()


        # HEADER

        if len(_body_bytes) % 2 != 0:
            self.has_padding = True
            _length = write_struct('UNORM', len(_body_bytes) + 5)
        else:
            _length = write_struct('UNORM', len(_body_bytes) + 4)

        _logical_record_type = write_struct('USHORT', self.logical_record_type)
        _attributes = write_struct('USHORT',
            int(
                str(int(self.is_eflr))\
               +str(int(self.has_predecessor_segment))\
               +str(int(self.has_successor_segment))\
               +str(int(self.is_encrypted))\
               +str(int(self.has_encryption_protocol))\
               +str(int(self.has_checksum))\
               +str(int(self.has_trailing_length))\
               +str(int(self.has_padding)),
               2
            )
        )

        _header_bytes = _length + _attributes + _logical_record_type


        _bytes = _header_bytes + _body_bytes
        if self.has_padding:
            _bytes += write_struct('USHORT', 1)

        return _bytes




class FileHeader(object):

    def __init__(self,
                 sequence_number:int=None,
                 _id:str=None):

        self.sequence_number = sequence_number
        self._id = _id
        self.origin_reference = None
        self.copy_number = 0
        self.name = None


    def get_as_bytes(self):
        # HEADER
        _length = write_struct('UNORM', 124)
        _attributes = write_struct('USHORT', int('10000000', 2))
        _type = write_struct('USHORT', 0)

        _header_bytes = _length + _attributes + _type

        # BODY
        _body_bytes = b''
        _body_bytes += Set(set_type='FILE-HEADER').get_as_bytes()
        _body_bytes += write_struct('USHORT', int('00110100', 2))
        _body_bytes += write_struct('USHORT', 15)
        _body_bytes += write_struct('ASCII', 'SEQUENCE-NUMBER')
        _body_bytes += write_struct('USHORT', 20)
        _body_bytes += write_struct('USHORT', int('00110100', 2))
        _body_bytes += write_struct('USHORT', 2)
        _body_bytes += write_struct('ASCII', 'ID')
        _body_bytes += write_struct('USHORT', 20)

        _body_bytes += write_struct('USHORT', int('01110000', 2))
        _body_bytes += write_struct('UVARI', self.origin_reference)
        _body_bytes += write_struct('USHORT', self.copy_number)
        _body_bytes += write_struct('IDENT', self.name)

        _body_bytes += write_struct('USHORT', int('00100001', 2))
        _body_bytes += write_struct('USHORT', 10)
        _body_bytes += get_ascii_bytes(self.sequence_number, 10, justify='right')
        _body_bytes += write_struct('USHORT', int('00100001', 2))
        _body_bytes += write_struct('USHORT', 65)
        _body_bytes += get_ascii_bytes(self._id, 65, justify='left')


        _bytes = _header_bytes + _body_bytes
        return _bytes


