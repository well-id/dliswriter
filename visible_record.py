from common.data_types import *


class VisibleRecord(object):
    '''
    
    QUOTE
    
        -> A Visible Record Length, expressed in terms of Representation Code UNORM (part of the Visible Envelope)
        
        -> A two-byte Format Version Field (part of the Visible Envelope, see section 2.3.6.2)
        
        -> One or more complete Logical Record Segments (part of the Logical Format)
    
    END Quote FROM: RP66 V1 -> Section 2.3.6.1 -> http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_1

    '''
    
    def __init__(self,
                 logical_record_segments:list=None):
        
        self.format_version = write_struct('USHORT',255) + write_struct('USHORT',1)
        self.logical_record_segments = [] 
        
        #TODO some of all three in bytes (2 (from visible_record_length) + 2 (from format_version) + sum of len of all logical_record_segments) 
        self.visible_record_length = None

# q1 = fs.read(4)
# q2 = fs.read(5)
# q3 = fs.read(6)
# q4 = fs.read(5)
# q5 = fs.read(60)
