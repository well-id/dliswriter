from common.data_types import struct_type_dict
from common.data_types import write_struct


class VisibleRecord(object):
    '''
    
    QUOTE
    
        -> A Visible Record Length, expressed in terms of Representation Code UNORM (part of the Visible Envelope)
        
        -> A two-byte Format Version Field (part of the Visible Envelope, see section 2.3.6.2)
        
        -> One or more complete Logical Record Segments (part of the Logical Format)
    
    END Quote FROM: RP66 V1 -> Section 2.3.6.1 -> http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_1

    '''
    
    def __init__(self):

        self.logical_record_segments = [] 

    def get_as_bytes(self):


        _body = b''
        for logical_record_segment in self.logical_record_segments:
            _body += logical_record_segment.get_as_bytes()

        _visible_record_length = write_struct('UNORM', len(_body) + 4)
        _format_version = write_struct('USHORT', 255) + write_struct('USHORT', 1)

        _bytes = _visible_record_length + _format_version + _body


        return _bytes



'''

TODO: When a logical record overflows a Visible Record, give the LR segment that overflew attribute "1" for the successor
which is the third attribute denoting "this is not the last segment". Then, start a new VR, define the remaining LR segment and 
give "1" for the predecessor attribute denoting "this is not the first segment"

Let's say you have FDATA:
    
    UNORM length 2096
    USHORT attributes '00000001'
    USHORT 0 (denoting IFLR FDATA logical record type)
    OBNAME for the frame reference
    FRAMENO 1
    .
    .
    ...data


Then you have another FDATA which must be length 2096 but will overflow after 324
THEN:
    
    UNORM length 324
    USHORT attributes '00100001'
    USHORT 0 (denoting IFLR FDATA logical record type)
    OBNAME for the frame reference
    FRAMENO 2
    .
    .
    ...data


Visible Record
    
    UNORM length 8192
    USHORT 255
    USHORT 1

FDATA continued
    
    UNORM length 2096
    USHORT attributes '01000001'
    USHORT 0 (denoting IFLR FDATA logical record type)
    .
    .
    ...data


Observe the 'Predecessor' and 'Successor' attributes,

AND NO OBNAME or FRAME NUMBER is required for the continued FDATA.


'''