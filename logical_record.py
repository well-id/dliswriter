from common.data_types import *


class LogicalRecordSegment(object):

    def __init__(self,
                 segment_length:int,
                 logical_record_type:int,
                 is_eflr:str,
                 has_predecessor_segment:str,
                 has_successor_segment:str,
                 is_encrypted:str,
                 has_encryption_protocol:str,
                 has_checksum:str,
                 has_trailing_length:str,
                 has_padding:str):


        '''  


        :segment_length --> Integer. Denotes the length of logical record segment in bytes.
        
        :logical_record_type --> Integer denoting the Logical Record Type (to be converted to USHORT). 
        For all record types please see: http://w3.energistics.org/rp66/v1/rp66v1_appa.html#A_2
        For example, logical_record_type=0 will be type FHLR, which is "File Header"
        

        ATTRIBUTES
        
        All 8 arguments listed below must be provided with a value of either "0" or "1".
        
        :is_eflr --> ACCEPTED VALUES "1" or "0", abbreviation for "Explicitly Formatted Logical Record"
        :has_predecessor_segment --> ACCEPTED VALUES "1" or "0"
        :has_successor_segment --> ACCEPTED VALUES "1" or "0"
        :is_encrypted --> ACCEPTED VALUES "1" or "0"
        :has_encryption_protocol --> ACCEPTED VALUES "1" or "0"
        :has_checksum --> ACCEPTED VALUES "1" or "0"
        :has_trailing_length --> ACCEPTED VALUES "1" or "0"
        :has_padding --> ACCEPTED VALUES "1" or "0"
        

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
        self.is_eflr = is_eflr # 1 or 0
        self.has_predecessor_segment = has_predecessor_segment # 1 or 0
        self.has_successor_segment = has_successor_segment # 1 or 0
        self.is_encrypted = is_encrypted # 1 or 0
        self.has_encryption_protocol = has_encryption_protocol # 1 or 0
        self.has_checksum = has_checksum # 1 or 0
        self.has_trailing_length = has_trailing_length # 1 or 0
        self.has_padding = has_padding # 1 or 0


    def get_bytes(self):
        _length = get_unorm(self.segment_length)
        _logical_record_type = get_ushort(self.logical_record_type)
        _attributes = get_ushort(
            int(
                self.is_eflr\
               +self.has_predecessor_segment\
               +self.has_successor_segment\
               +self.is_encrypted\
               +self.has_encryption_protocol\
               +self.has_checksum\
               +self.has_trailing_length\
               +self.has_padding,
               2
            )
        )

        return _length + _attributes + _logical_record_type




    # def get_trailer_length(self):

    #     trailer_lengt

# s = LogicalRecordSegment(124,0,"1","0","0","0","0","0","0","0")
# print(s.get_bytes())