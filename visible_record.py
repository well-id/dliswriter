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