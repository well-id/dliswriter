from common.data_types import *


class VisibleRecord(object):
    '''
    
    QUOTE
    
        -> A Visible Record Length, expressed in terms of Representation Code UNORM (part of the Visible Envelope)
        
        -> A two-byte Format Version Field (part of the Visible Envelope, see section 2.3.6.2)
        
        -> One or more complete Logical Record Segments (part of the Logical Format)
    
    END Quote FROM: RP66 V1 -> Section 2.3.6.1 -> http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_1

    '''
    
    def __init__(self, visible_record_length, logical_record_segments):
        self.visible_record_length = visible_record_length
        self.format_version = get_ushort(255) + get_ushort(1)
        self.logical_record_segments = [] 

# q1 = fs.read(4)
# q2 = fs.read(5)
# q3 = fs.read(6)
# q4 = fs.read(5)
# q5 = fs.read(60)
