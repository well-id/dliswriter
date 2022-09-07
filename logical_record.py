from datetime import datetime

from common.data_types import struct_type_dict
from common.data_types import write_struct

from utils.converters import get_ascii_bytes
from utils.converters import get_representation_code

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


class IFLR(object):

    def __init__(self):
        pass


class EFLR(object):

    def __init__(self,
                 set_type:str=None,
                 set_name:str=None,
                 origin_reference:int=None,
                 copy_number:int=0,
                 object_name:str=None,
                 has_padding:bool=False):

        self.set_type = set_type
        self.set_name = set_name
        self.origin_reference = origin_reference
        self.copy_number = copy_number
        self.object_name = object_name
        self.has_padding = has_padding


    def finalize_bytes(self, logical_record_type, _body):
        # HEADER
        if len(_body) % 2 != 0:
            self.has_padding = True
            _length = write_struct('UNORM', len(_body) + 5)
        else:
            _length = write_struct('UNORM', len(_body) + 4)

        _logical_record_type = write_struct('USHORT', logical_record_type)
        _attributes = write_struct('USHORT', int('1000000' + str(int(self.has_padding)), 2))

        _header = _length + _attributes + _logical_record_type


        _bytes = _header + _body
        if self.has_padding:
            _bytes += write_struct('USHORT', 1)

        return _bytes


    def get_obname_only(self):
        return write_struct('OBNAME', (self.origin_reference,
                                       self.copy_number,
                                       self.object_name))


    def write_absent_attribute(self):
        return write_struct('USHORT', int('00000000', 2))


class FileHeader(object):

    def __init__(self,
                 sequence_number:int=1,
                 _id:str='DEFAULT FHLR'):

        self.sequence_number = sequence_number
        self._id = _id
        
        self.origin_reference = None
        self.copy_number = 0
        self.object_name = '0'

        self.set_type = 'FILE-HEADER'


    def get_as_bytes(self):
        # HEADER
        _length = write_struct('UNORM', 124)
        _attributes = write_struct('USHORT', int('10000000', 2))
        _type = write_struct('USHORT', 0)

        _header_bytes = _length + _attributes + _type

        # BODY
        _body_bytes = b''
        _body_bytes += Set(set_type='FILE-HEADER').get_as_bytes()
        
        # TEMPLATE
        _body_bytes += write_struct('USHORT', int('00110100', 2))
        _body_bytes += write_struct('ASCII', 'SEQUENCE-NUMBER')
        _body_bytes += write_struct('USHORT', 20)
        
        _body_bytes += write_struct('USHORT', int('00110100', 2))
        _body_bytes += write_struct('ASCII', 'ID')
        _body_bytes += write_struct('USHORT', 20)

        # OBJECT
        _body_bytes += write_struct('USHORT', int('01110000', 2))
        _body_bytes += write_struct('OBNAME', (self.origin_reference,
                                               self.copy_number,
                                               self.object_name))

        # ATTRIBUTES
        _body_bytes += write_struct('USHORT', int('00100001', 2))
        _body_bytes += write_struct('USHORT', 10)
        _body_bytes += get_ascii_bytes(self.sequence_number, 10, justify='right')
        _body_bytes += write_struct('USHORT', int('00100001', 2))
        _body_bytes += write_struct('USHORT', 65)
        _body_bytes += get_ascii_bytes(self._id, 65, justify='left')


        _bytes = _header_bytes + _body_bytes
        
        return _bytes


class Origin(EFLR):
    
    def __init__(self,
                 file_id:str=None,
                 file_set_name:str=None,
                 file_set_number:int=None,
                 file_number:int=None,
                 file_type:str=None,
                 product:str=None,
                 version:str=None,
                 programs:str=None,
                 creation_time=None,
                 order_number:str=None,
                 descent_number:int=None,
                 run_number:int=None,
                 well_id:int=None,
                 well_name:str=None,
                 field_name:str=None,
                 producer_code:int=None,
                 producer_name:str=None,
                 company:str=None,
                 name_space_name:str=None,
                 name_space_version:int=None):

        super().__init__()

        self.file_id = file_id
        self.file_set_name = file_set_name
        self.file_set_number = file_set_number
        self.file_number = file_number
        self.file_type = file_type
        self.product = product
        self.version = version
        self.programs = programs
        self.creation_time = creation_time
        self.order_number = order_number
        self.descent_number = descent_number
        self.run_number = run_number
        self.well_id = well_id
        self.well_name = well_name
        self.field_name = field_name
        self.producer_code = producer_code
        self.producer_name = producer_name
        self.company = company
        self.name_space_name = name_space_name
        self.name_space_version = name_space_version


        self.set_type = 'ORIGIN'


    def get_as_bytes(self):
        _body = b''

        # Set
        _body += Set(set_type='ORIGIN', set_name=self.set_name).get_as_bytes()

        # Template
        if self.file_id:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-ID')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.file_set_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-SET-NAME')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.file_set_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-SET-NUMBER')
            _body += write_struct('USHORT', get_representation_code('UVARI'))
        
        if self.file_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-NUMBER')
            _body += write_struct('USHORT', get_representation_code('UVARI'))
        
        if self.file_type:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-TYPE')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.product:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PRODUCT')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.version:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'VERSION')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.programs:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PROGRAMS')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.creation_time:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'CREATION-TIME')
            _body += write_struct('USHORT', get_representation_code('DTIME'))
        
        if self.order_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ORDER-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.descent_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'DESCENT-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.run_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'RUN-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.well_id:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'WELL-ID')
            _body += write_struct('USHORT', get_representation_code('UVARI'))
        
        if self.well_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'WELL-NAME')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.field_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FIELD-NAME')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.producer_code:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PRODUCER-CODE')
            _body += write_struct('USHORT', get_representation_code('UNORM'))
        
        if self.producer_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PRODUCER-NAME')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.company:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'COMPANY')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.name_space_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'NAME-SPACE-NAME')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.name_space_version:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'NAME-SPACE-VERSION')
            _body += write_struct('USHORT', get_representation_code('UVARI'))


        # OBJECT
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # ATTRIBUTES
        
        if self.file_id:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.file_id)
        
        if self.file_set_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.file_set_name)
        
        if self.file_set_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UVARI', self.file_set_number)
        
        if self.file_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UVARI', self.file_number)
        
        if self.file_type:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.file_type)
        
        if self.product:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.product)
        
        if self.version:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.version)
        
        if self.programs:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.programs)
        
        if self.creation_time:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('DTIME', self.creation_time)
        
        if self.order_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.order_number)
        
        if self.descent_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.descent_number)
        
        if self.run_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.run_number)
        
        if self.well_id:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UVARI', self.well_id)
        
        if self.well_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.well_name)
        
        if self.field_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.field_name)
        
        if self.producer_code:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UNORM', self.producer_code)
        
        if self.producer_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.producer_name)
        
        if self.company:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.company)
        
        if self.name_space_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.name_space_name)
        
        if self.name_space_version:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UVARI', self.name_space_version)


        # HEADER
        return self.finalize_bytes(1, _body)


class WellReferencePoint(EFLR):

    def __init__(self,
                 permanent_datum:str=None,
                 vertical_zero:str=None,
                 permanent_datum_elevation:float=None,
                 above_permanent_datum:float=None,
                 magnetic_declination:float=None,
                 coordinate_1_name:str=None,
                 coordinate_1_value:float=None,
                 coordinate_2_name:str=None,
                 coordinate_2_value:float=None,
                 coordinate_3_name:str=None,
                 coordinate_3_value:float=None):

        super().__init__()

        self.permanent_datum = permanent_datum
        self.vertical_zero = vertical_zero
        self.permanent_datum_elevation = permanent_datum_elevation
        self.above_permanent_datum = above_permanent_datum
        self.magnetic_declination = magnetic_declination
        self.coordinate_1_name = coordinate_1_name
        self.coordinate_1_value = coordinate_1_value
        self.coordinate_2_name = coordinate_2_name
        self.coordinate_2_value = coordinate_2_value
        self.coordinate_3_name = coordinate_3_name
        self.coordinate_3_value = coordinate_3_value

        self.set_type = 'WELL-REFERENCE'

    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='WELL-REFERENCE', set_name=self.set_name).get_as_bytes()


        # TEMPLATE
        if self.permanent_datum:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'PERMANENT-DATUM')
        if self.vertical_zero:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'VERTICAL-ZERO')
        if self.permanent_datum_elevation:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'PERMANENT-DATUM-ELEVATION')
        if self.above_permanent_datum:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'ABOVE-PERMANENT-DATUM')
        if self.magnetic_declination:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'MAGNETIC-DECLINATION')
        if self.coordinate_1_name:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-1-NAME')
        if self.coordinate_1_value:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-1-VALUE')
        if self.coordinate_2_name:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-2-NAME')
        if self.coordinate_2_value:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-2-VALUE')
        if self.coordinate_3_name:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-3-NAME')
        if self.coordinate_3_value:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-3-VALUE')


        # Object
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # ATTRIBUTES

        if self.permanent_datum:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.permanent_datum)

        if self.vertical_zero:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.vertical_zero)

        if self.permanent_datum_elevation:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.permanent_datum_elevation)

        if self.above_permanent_datum:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.above_permanent_datum)

        if self.magnetic_declination:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.magnetic_declination)

        if self.coordinate_1_name:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.coordinate_1_name)

        if self.coordinate_1_value:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.coordinate_1_value)

        if self.coordinate_2_name:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.coordinate_2_name)

        if self.coordinate_2_value:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.coordinate_2_value)

        if self.coordinate_3_name:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.coordinate_3_name)

        if self.coordinate_3_value:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.coordinate_3_value)


        return self.finalize_bytes(1, _body)


class Axis(EFLR):

    def __init__(self,
                 axis_id:str=None,
                 coordinates:list=None,
                 coordinates_struct_type:str='FDOUBL',
                 spacing:int=None):
        '''
        
        
        :axis_id -> Identifier
        
        :coordinates -> A list of coordinates (please see the quote below)
        
        :coordinates_struct_type -> Default data type is float, but
        if you pass string, this attribute must be set to 'ASCII' or 'IDENT'.
        (see below quote)

        :spacing -> signed spacing along the axis between successive coordinates,
        beginning at the last coordinate value specified by the coordinates attribute.


        QUOTE
            The Coordinates Attribute specifies explicit coordinate values 
            along a coordinate axis. 
            These values may be numeric (i.e., for non-uniform coordinate spacing),
            or they may be textual identifiers, for example "Near" and "Far".
            If the Coordinates Value has numeric Elements, 
            then they must occur in order of increasing or decreasing value.
            The Count of the Coordinates Attribute need not agree 
            with the number of array elements along this axis 
            specified by a related Dimension Attribute.
        END QUOTE FROM ->  RP66 V1 Section 5.3.1 -> http://w3.energistics.org/rp66/v1/rp66v1_sec5.html#5_3_1

        
        References:
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec5.html#5_3_1

        '''

        super().__init__()

        self.axis_id = axis_id
        if coordinates:
            self.coordinates = coordinates
        else:
            self.coordinates = []
        self.coordinates_struct_type = coordinates_struct_type
        self.spacing = spacing

        self.set_type = 'AXIS'

    def get_as_bytes(self):
        _body = b''

        # SET
        _body += Set(set_type='AXIS', set_name=self.set_name).get_as_bytes()

        # TEMPLATE        
        if self.axis_id:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'AXIS-ID')
        
        if self.coordinates:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATES')
        
        if self.spacing:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'SPACING')


        # OBJECT
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # ATTRIBUTES (VALUES)
        if self.axis_id:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', get_representation_code('IDENT'))
            _body += write_struct('IDENT', self.axis_id)

        if self.coordinates:

            if len(self.coordinates) > 1:
                _body += write_struct('USHORT', int('00101101', 2))
                _body += write_struct('UVARI', len(self.coordinates))

                for coord in self.coordinates:
                    _body += write_struct(self.coordinates_struct_type, coord)

            else:
                _body += write_struct('USHORT', int('00100101', 2))
                _body += write_struct('USHORT', get_representation_code(self.coordinates_struct_type))
                _body += write_struct(get_representation_code(self.coordinates_struct_type), self.coordinates[0])

        if self.spacing:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', get_representation_code('SLONG'))
            _body += write_struct('SLONG', self.spacing)


        return self.finalize_bytes(2, _body)


class LongName(EFLR):

    def __init__(self,
                 general_modifier:str=None,
                 quantity:str=None,
                 quantity_modifier:str=None,
                 altered_form:str=None,
                 entity:str=None,
                 entity_modifier:str=None,
                 entity_number:str=None,
                 entity_part:str=None,
                 entity_part_number:str=None,
                 generic_source:str=None,
                 source_part:str=None,
                 source_part_number:str=None,
                 conditions:str=None,
                 standard_symbol:str=None,
                 private_symbol:str=None):


        super().__init__()

        self.general_modifier = general_modifier
        self.quantity = quantity
        self.quantity_modifier = quantity_modifier
        self.altered_form = altered_form
        self.entity = entity
        self.entity_modifier = entity_modifier
        self.entity_number = entity_number
        self.entity_part = entity_part
        self.entity_part_number = entity_part_number
        self.generic_source = generic_source
        self.source_part = source_part
        self.source_part_number = source_part_number
        self.conditions = conditions
        self.standard_symbol = standard_symbol
        self.private_symbol = private_symbol


        self.set_type = 'LONG-NAME'


    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='LONG-NAME', set_name=self.set_name).get_as_bytes()


        if self.general_modifier:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'GENERAL-MODIFIER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.quantity:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'QUANTITY')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.quantity_modifier:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'QUANTITY-MODIFIER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.altered_form:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ALTERED-FORM')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity_modifier:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY-MODIFIER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity_part:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY-PART')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity_part_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY-PART-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.generic_source:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'GENERIC-SOURCE')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.source_part:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'SOURCE-PART')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.source_part_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'SOURCE-PART-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.conditions:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'CONDITIONS')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.standard_symbol:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'STANDARD-SYMBOL')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.private_symbol:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PRIVATE-SYMBOL')
            _body += write_struct('USHORT', get_representation_code('ASCII'))


        # Object
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # ATTRIBUTES
        if self.general_modifier:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.general_modifier)
            
        if self.quantity:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.quantity)
            
        if self.quantity_modifier:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.quantity_modifier)
            
        if self.altered_form:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.altered_form)
            
        if self.entity:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity)
            
        if self.entity_modifier:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity_modifier)
            
        if self.entity_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity_number)
            
        if self.entity_part:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity_part)
            
        if self.entity_part_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity_part_number)
            
        if self.generic_source:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.generic_source)
            
        if self.source_part:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.source_part)
            
        if self.source_part_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.source_part_number)
            
        if self.conditions:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.conditions)
            
        if self.standard_symbol:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.standard_symbol)
            
        if self.private_symbol:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.private_symbol)
            


        return self.finalize_bytes(9, _body)


# !!!!! COMPLETE Source Attribute (OBJREF)
class Channel(EFLR):
    
    def __init__(self,
                 long_name:str=None,
                 properties:list=None,
                 representation_code:str=None,
                 units:str=None,
                 dimension:list=None,
                 axis=None,
                 element_limit:list=None,
                 source=None):

        super().__init__()

        self.long_name = long_name
        self.properties = properties
        self.representation_code = representation_code
        self.units = units
        self.dimension = dimension
        self.axis = axis
        self.element_limit = element_limit
        self.source = source


        self.set_type = 'CHANNEL'

    def get_as_bytes(self):
        _bytes = b''
        _bytes += write_struct('USHORT', int('01110000', 2))
        _bytes += write_struct('OBNAME', (self.origin_reference,
                                          self.copy_number,
                                          self.object_name))

        if self.long_name:
            _bytes += write_struct('USHORT', int('00100001', 2))
            _bytes += write_struct('ASCII', self.long_name)
        else:
            _bytes += self.write_absent_attribute()

        
        if self.properties:
            if len(self.properties) > 1:
                _bytes += write_struct('USHORT', int('00101001', 2))
                _bytes += write_struct('UVARI', len(self.properties))

                for prop in self.properties:
                    _bytes += write_struct('IDENT', prop)

            else:
                _bytes += write_struct('USHORT', int('00100001', 2))
                _bytes += write_struct('IDENT', self.dimension[0])
        else:
            _bytes += self.write_absent_attribute()


        
        if self.representation_code:
            _bytes += write_struct('USHORT', int('00100001', 2))
            _bytes += write_struct('USHORT', get_representation_code(self.representation_code))

        else:
            _bytes += self.write_absent_attribute()
        

        if self.units:
            _bytes += write_struct('USHORT', int('00100001', 2))
            _bytes += write_struct('UNITS', self.units)

        else:
            _bytes += self.write_absent_attribute()
        

        if self.dimension:
            if len(self.dimension) > 1:
                _bytes += write_struct('USHORT', int('00101001', 2))
                _bytes += write_struct('UVARI', len(self.dimension))
                for dim in self.dimension:
                    _bytes += write_struct('UVARI', dim)

            else:
                _bytes += write_struct('USHORT', int('00100001', 2))
                _bytes += write_struct('UVARI', self.dimension[0])
            
        else:
            _bytes += self.write_absent_attribute()
        

        if self.axis:
            _bytes += write_struct('USHORT', int('00100001', 2))
            _bytes += self.axis.get_obname_only()

        else:
            _bytes += self.write_absent_attribute()
        

        if self.element_limit:
            if len(self.element_limit) > 1:
                _bytes += write_struct('USHORT', int('00101001', 2))
                _bytes += write_struct('UVARI', len(self.element_limit))
                for el in self.element_limit:
                    _bytes += write_struct('UVARI', el)
            else:
                _bytes += write_struct('USHORT', int('00100001', 2))
                _bytes += write_struct('UVARI', self.element_limit[0])
            
        else:
            _bytes += self.write_absent_attribute()
        

        # NEEDS REFACTORING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.source:
            pass
        else:
            _bytes += self.write_absent_attribute()

        return _bytes


class ChannelLogicalRecord(EFLR):
    
    def __init__(self,
                 channels:list=None):

        super().__init__()

        if channels:
            self.channels = channels
        else:
            self.channels = []
    

        self.set_type = 'CHANNEL'

    def get_as_bytes(self):
        _body = b''

        # SET
        _body += Set(set_type='CHANNEL', set_name=self.set_name).get_as_bytes()

        # TEMPLATE

        
        # long_name:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'LONG-NAME')
        _body += write_struct('USHORT', get_representation_code('ASCII'))
    
        # properties:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'PROPERTIES')
        _body += write_struct('USHORT', get_representation_code('IDENT'))
    
        # representation_code:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'REPRESENTATION-CODE')
        _body += write_struct('USHORT', get_representation_code('USHORT'))
    
        # units:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'UNITS')
        _body += write_struct('USHORT', get_representation_code('UNITS'))
    
        # dimension:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'DIMENSION')
        _body += write_struct('USHORT', get_representation_code('UVARI'))
    
        # axis:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'AXIS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
    
        # element_limit:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'ELEMENT-LIMIT')
        _body += write_struct('USHORT', get_representation_code('UVARI'))
    
        # source:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'SOURCE')
        _body += write_struct('USHORT', get_representation_code('OBJREF'))


        # add each Channel object here

        for channel_object in self.channels:
            _body += channel_object.get_as_bytes()


        return self.finalize_bytes(3, _body)


class Frame(EFLR):

    def __init__(self,
                 description:str=None,
                 channels:list=None,
                 index_type:str=None,
                 direction:str=None,
                 spacing:float=None,
                 spacing_units:str=None,
                 encrypted:bool=False,
                 index_min:int=None,
                 index_max:int=None):

        super().__init__()

        self.description = description
        if channels:
            self.channels = channels
        else:
            self.channels = []
        self.index_type = index_type
        self.direction = direction
        self.spacing = spacing
        self.spacing_units = spacing_units
        self.encrypted = encrypted
        self.index_min = index_min
        self.index_max = index_max


        self.set_type = 'FRAME'

    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='FRAME').get_as_bytes()

        # TEMPLATE
        if self.description:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'DESCRIPTION')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.channels:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'CHANNELS')
            _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        if self.index_type:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'INDEX-TYPE')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.direction:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'DIRECTION')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.spacing:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'SPACING')
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
        
        if self.encrypted:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENCRYPTED')
            _body += write_struct('USHORT', get_representation_code('USHORT'))
        
        if self.index_min:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'INDEX-MIN')
            _body += write_struct('USHORT', get_representation_code('SLONG'))
        
        if self.index_max:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'INDEX-MAX')
            _body += write_struct('USHORT', get_representation_code('SLONG'))

        # OBJECT
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))

        # ATTRIBUTES
        if self.description:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.description)

        if self.channels:
            if len(self.channels) > 1:
                _body += write_struct('USHORT', int('00101001', 2))
                _body += write_struct('UVARI', len(self.channels))

                for channel in self.channels:
                    _body += channel.get_obname_only()
            else:
                _body += write_struct('USHORT', int('00100001', 2))
                _body += self.channels[0].get_obname_only()

        if self.index_type:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.index_type)

        if self.direction:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.direction)

        if self.spacing:
            if self.spacing_units:
                _body += write_struct('USHORT', int('00100011', 2))
                _body += write_struct('UNITS', self.spacing_units)
                _body += write_struct('FDOUBL', self.spacing)
            else:
                _body += write_struct('USHORT', int('00100001', 2))
                _body += write_struct('FDOUBL', self.spacing)

        if self.encrypted:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('USHORT', int(self.encrypted))

        if self.index_min:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('SLONG', self.index_min)

        if self.index_max:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('SLONG', self.index_max)


        return self.finalize_bytes(4, _body)


class FrameData(IFLR):

    def __init__(self,
                 frame=None,
                 frame_number:int=None,
                 slots=None):

        '''
    
        FrameData is an Implicitly Formatted Logical Record (IFLR)

        Each FrameData object begins with a reference to the Frame object
        that they belong to using OBNAME.

        :frame -> A Frame(EFLR) object instance
        :position -> Auto-assigned integer denoting the position of the FrameData
        
        :slots -> Represents a row in the dataframe. If there are 3 channels, slots will be the array
        of values at the corresponding index for those channels.

        '''


        self.frame = frame
        self.frame_number = frame_number # UVARI
        self.slots = slots # np.ndarray


        self.set_type = 'FDATA'

    def finalize_bytes(self, _body):
        
        
        _length = len(_body) + 4
        if _length % 2 == 0:
            _attributes = write_struct('USHORT', int('00000000', 2))
            _has_padding = False
        else:
            _attributes = write_struct('USHORT', int('00000001', 2))
            _length += 1
            _has_padding = True

        
        _header = b''
        _header += write_struct('UNORM', _length)
        _header += _attributes
        _header += write_struct('USHORT', 0) # Logical Record Type



        _bytes = _header + _body

        if _has_padding:
            _bytes += write_struct('USHORT', 0)

        return _bytes


    def get_as_bytes(self):

        _body = b''

        _body += self.frame.get_obname_only()
        _body += write_struct('UVARI', self.frame_number)
        
        for i in range(len(self.slots)):

            data = self.slots[i] # NP array
            # data = list(data.flatten('F'))

            # Get representation code from corresponding Channel
            representation_code = self.frame.channels[i].representation_code

            if type(data) == list:
                for value in data:
                    _body += write_struct(representation_code, value)

            else:
                _body += write_struct(representation_code, data)

        return self.finalize_bytes(_body)


# INCOMPLETE
class Path(EFLR):

    def __init__(self):
        super().__init__()


        self.set_type = 'PATH'


class Zone(EFLR):

    def __init__(self,
                 description:str=None,
                 domain:str=None,
                 maximum=None,
                 minimum=None,
                 representation_code=None,
                 units=None):


        '''

        :description -> str

        :domain -> 3 options:
            BOREHOLE-DEPTH
            TIME
            VERTICAL-DEPTH

        :maximum -> Depending on the 'domain' attribute, this is either
        max-depth (dtype: float) or the latest time (dtype: datetime.datetime)

        :minimum -> Dependng on the 'domain' attribute, this is either
        min-depth (dtype: float) or the earlieast time (dtype: datetime.datetime)

        '''


        super().__init__()
        self.description = description

        self.domain = domain
        self.maximum = maximum
        self.minimum = minimum
        self.representation_code = representation_code
        self.units = units


        self.set_type = 'ZONE'

    def validate(self):

        if self.domain is not None and self.domain not in ['BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH']:
            exception_message = ('\n\nDomain attribute for zone must be one of the following:\n'
                                 '\t1. BOREHOLE-DEPTH\n\t2. TIME\n\t3. VERTICAL-DEPTH\n'
                                 'Reference: http://w3.energistics.org/rp66/v1/rp66v1_sec5.html#5_8_1\n\n')
            raise Exception(exception_message)

        if self.domain in ['BOREHOLE-DEPTH', 'VERTICAL-DEPTH']:
            self.representation_code = 'FDOUBL'
            if self.maximum is not None and type(self.maximum) != float:
                exception_message = (f'\n\nWhen the "domain" attribute is {self.domain}, '
                                     '"maximum" attribute must be a float\n\n')
                raise Exception(exception_message)

            if self.minimum is not None and type(self.minimum) != float:
                exception_message = (f'\n\nWhen the "domain" attribute is {self.domain}, '
                                     '"minimum" attribute must be a float\n\n')
                raise Exception(exception_message)

        elif self.domain == 'TIME':
            self.representation_code = 'DTIME'
            if self.maximum is not None and type(self.maximum) != datetime:
                exception_message = (f'\n\nWhen the "domain" attribute is {self.domain}, '
                                     '"maximum" attribute must be a datetime.datetime instance\n'
                                     'eg. datetime.datetime.now()\n\n')
                raise Exception(exception_message)

            if self.minimum is not None and type(self.minimum) != datetime:
                exception_message = (f'\n\nWhen the "domain" attribute is {self.domain}, '
                                     '"minimum" attribute must be a datetime.datetime instance\n'
                                     'eg. datetime.datetime.now()\n\n')
                raise Exception(exception_message)



    def get_as_bytes(self):

        self.validate()

        _body = b''

        # SET
        _body += Set(set_type='ZONE', set_name=self.set_name).get_as_bytes()


        # TEMPLATE
        if self.description:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'DESCRIPTION')
            _body += write_struct('USHORT', get_representation_code('ASCII'))

        if self.domain:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'DOMAIN')
            _body += write_struct('USHORT', get_representation_code('IDENT'))

        if self.maximum:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'MAXIMUM')
            _body += write_struct('USHORT', get_representation_code(self.representation_code))

        if self.minimum:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'MINIMUM')
            _body += write_struct('USHORT', get_representation_code(self.representation_code))


        # OBJECT
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # VALUES
        if self.description:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.description)
        
        if self.domain:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.domain)
        
        if self.maximum:
            if self.units:
                _body += write_struct('USHORT', int('00100011', 2))
                _body += write_struct('UNITS', self.units)
            else:
                _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct(self.representation_code, self.maximum)
        
        if self.minimum:
            if self.units:
                _body += write_struct('USHORT', int('00100011', 2))
                _body += write_struct('UNITS', self.units)
            else:
                _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct(self.representation_code, self.minimum)



        return self.finalize_bytes(5, _body)


class Parameter(EFLR):

    def __init__(self,
                 long_name:str=None,
                 dimension:list=None,
                 axis=None, # Not enough info on RP66 V1
                 zones:list=None,
                 values:list=None,
                 representation_code:str=None,
                 units:str=None):

        super().__init__()

        self.long_name = long_name
        
        if dimension:
            self.dimension = dimension
        else:
            self.dimension = []

        self.axis = axis
        
        if zones:
            self.zones = zones
        else:
            self.zones = []
        
        if values:
            self.values = values
        else:
            self.values = []


        self.representation_code = representation_code
        self.units = units

        self.set_type = 'PARAMETER'

    def get_as_bytes(self):
        _body = b''

        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))

        if self.long_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.long_name)
        else:
            _body += self.write_absent_attribute()

        if self.dimension:
            if len(self.dimension) > 1:
                _body += write_struct('USHORT', int('00101001', 2))
                _body += write_struct('UVARI', len(self.dimension))
            else:
                _body += write_struct('USHORT', int('00100001', 2))

            for dim in self.dimension:
                _body += write_struct('UVARI', dim)
        else:
            _body += self.write_absent_attribute()

        if self.axis:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += self.axis.get_obname_only()
        else:
            _body += self.write_absent_attribute()

        if self.zones:
            if len(self.zones) > 1:
                _body += write_struct('USHORT', int('00101001', 2))
                _body += write_struct('UVARI', len(self.zones))
            else:
                _body += write_struct('USHORT', int('00100001', 2))

            for zone in self.zones:
                _body += zone.get_obname_only()
        else:
            _body += self.write_absent_attribute()


        if self.values:
            if self.units:
                _body += write_struct('USHORT', int('00101111', 2))
                _body += write_struct('UVARI', len(self.values))
                _body += write_struct('USHORT', get_representation_code(self.representation_code))
                _body += write_struct('UNITS', self.units)
            else:
                _body += write_struct('USHORT', int('00101101', 2))
                _body += write_struct('UVARI', len(self.values))
                _body += write_struct('USHORT', get_representation_code(self.representation_code))
            for val in self.values:
                _body += write_struct(self.representation_code, val)
        else:
            _body += self.write_absent_attribute()


        return _body


class ParameterLogicalRecord(EFLR):

    def __init__(self,
                 parameters:list=None):

        super().__init__()

        if parameters:
            self.parameters = parameters
        else:
            self.parameters = []


        self.set_type = 'PARAMETER'

    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='PARAMETER', set_name=self.set_name).get_as_bytes()

        # TEMPLATE
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'LONG-NAME')
        _body += write_struct('USHORT', get_representation_code('ASCII'))

        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'DIMENSION')
        _body += write_struct('USHORT', get_representation_code('UVARI'))

        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'AXIS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'ZONES')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'VALUES')


        # VALUES
        for parameter in self.parameters:
            _body += parameter.get_as_bytes()


        return self.finalize_bytes(5, _body)


class Equipment(EFLR):

    def __init__(self,
                 trademark_name:str=None,
                 status:bool=True,
                 _type:str=None,
                 serial_number:str=None,
                 location:str=None,
                 height:float=None,
                 height_units:float=None,
                 length:float=None,
                 length_units:float=None,
                 minimum_diameter:float=None,
                 minimum_diameter_units:float=None,
                 maximum_diameter:float=None,
                 maximum_diameter_units:float=None,
                 volume:float=None,
                 volume_units:float=None,
                 weight:float=None,
                 weight_units:float=None,
                 hole_size:float=None,
                 hole_size_units:float=None,
                 pressure:float=None,
                 pressure_units:float=None,
                 temperature:float=None,
                 temperature_units:float=None,
                 vertical_depth:float=None,
                 vertical_depth_units:float=None,
                 radial_drift:float=None,
                 radial_drift_units:float=None,
                 angular_drift:float=None,
                 angular_drift_units:float=None):



        super().__init__()


        self.trademark_name = trademark_name
        self.status = status
        self._type = _type
        self.serial_number = serial_number
        self.location = location
        self.height = height
        self.height_units = height_units
        self.length = length
        self.length_units = length_units
        self.minimum_diameter = minimum_diameter
        self.minimum_diameter_units = minimum_diameter_units
        self.maximum_diameter = maximum_diameter
        self.maximum_diameter_units = maximum_diameter_units
        self.volume = volume
        self.volume_units = volume_units
        self.weight = weight
        self.weight_units = weight_units
        self.hole_size = hole_size
        self.hole_size_units = hole_size_units
        self.pressure = pressure
        self.pressure_units = pressure_units
        self.temperature = temperature
        self.temperature_units = temperature_units
        self.vertical_depth = vertical_depth
        self.vertical_depth_units = vertical_depth_units
        self.radial_drift = radial_drift
        self.radial_drift_units = radial_drift_units
        self.angular_drift = angular_drift
        self.angular_drift_units = angular_drift_units


        self.set_type = 'EQUIPMENT'


    def get_as_bytes(self):

        # Body
        _body = b''

        # Set
        _body += Set(set_type='EQUIPMENT', set_name=self.set_name).get_as_bytes()

        # Template
        if self.trademark_name:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'TRADEMARK-NAME')

        if self.status:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'STATUS')

        if self._type:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'TYPE')

        if self.serial_number:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'SERIAL-NUMBER')

        if self.location:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'LOCATION')


        if self.height:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'HEIGHT')
        
        if self.length:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'LENGTH')
        
        if self.minimum_diameter:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'MINIMUM-DIAMETER')
        
        if self.maximum_diameter:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'MAXIMUM-DIAMETER')
        
        if self.volume:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'VOLUME')
        
        if self.weight:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'WEIGHT')
       
        if self.hole_size:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'HOLE-SIZE')
        
        if self.pressure:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'PRESSURE')
        
        if self.temperature:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'TEMPERATURE')
        
        if self.vertical_depth:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'VERTICAL-DEPTH')
        
        if self.radial_drift:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'RADIAL-DRIFT')
        
        if self.angular_drift:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'ANGULAR-DRIFT')


        # Object
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # Attributes (VALUES)
        
        if self.trademark_name:
            print('Creating TM ATTTTTRRR')
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', get_representation_code('ASCII'))
            _body += write_struct('IDENT', self.trademark_name)

        if self.status:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', get_representation_code('STATUS'))
            _body += write_struct('STATUS', int(self.status))

        if self._type:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', get_representation_code('IDENT'))
            _body += write_struct('IDENT', self._type)

        if self.serial_number:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', get_representation_code('IDENT'))
            _body += write_struct('IDENT', self.serial_number)

        if self.location:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', get_representation_code('IDENT'))
            _body += write_struct('IDENT', self.location)

        if self.height:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.height_units:
                units = write_struct('IDENT', self.height_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.height)

        if self.length:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.length_units:
                units = write_struct('IDENT', self.length_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.length)

        if self.minimum_diameter:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.minimum_diameter_units:
                units = write_struct('IDENT', self.minimum_diameter_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.minimum_diameter)

        if self.maximum_diameter:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.maximum_diameter_units:
                units = write_struct('IDENT', self.maximum_diameter_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.maximum_diameter)

        if self.volume:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.volume_units:
                units = write_struct('IDENT', self.volume_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.volume)

        if self.weight:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.weight_units:
                units = write_struct('IDENT', self.weight_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.weight)

        if self.hole_size:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.hole_size_units:
                units = write_struct('IDENT', self.hole_size_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.hole_size)

        if self.pressure:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.pressure_units:
                units = write_struct('IDENT', self.pressure_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.pressure)

        if self.temperature:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.temperature_units:
                units = write_struct('IDENT', self.temperature_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.temperature)

        if self.vertical_depth:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.vertical_depth_units:
                units = write_struct('IDENT', self.vertical_depth_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.vertical_depth)

        if self.radial_drift:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.radial_drift_units:
                units = write_struct('IDENT', self.radial_drift_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.radial_drift)

        if self.angular_drift:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.angular_drift_units:
                units = write_struct('IDENT', self.angular_drift_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.angular_drift)



        return self.finalize_bytes(5, _body)


class Tool(EFLR):

    def __init__(self,
                 description:str=None,
                 trademark_name:str=None,
                 generic_name:str=None,
                 parts:list=None,
                 status:bool=True,
                 channels:list=None,
                 parameters:list=None):

        super().__init__()
        self.description = description
        self.trademark_name = trademark_name
        self.generic_name = generic_name
        if parts:
            self.parts = parts
        else:
            self.parts = []
        self.status = status
        if channels:
            self.channels = channels
        else:
            self.channels = []

        if parameters:
            self.parameters = parameters
        else:
            self.parameters = []


        self.set_type = 'TOOL'

    def get_as_bytes(self):
        
        _body = b''

        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))

        
        if self.description:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.description)
        else:
            _body += self.write_absent_attribute()
        
        if self.trademark_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.trademark_name)
        else:
            _body += self.write_absent_attribute()
        
        if self.generic_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.generic_name)
        else:
            _body += self.write_absent_attribute()
        
        if self.parts:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.parts))
            for obj in self.parts:
                _body += obj.get_obname_only()
        else:
            _body += self.write_absent_attribute()
        
        if self.status:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('USHORT', int(self.status))
        else:
            _body += self.write_absent_attribute()
        
        if self.channels:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.channels))
            for obj in self.channels:
                _body += obj.get_obname_only()
        else:
            _body += self.write_absent_attribute()
        
        if self.parameters:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.parameters))
            for obj in self.parameters:
                _body += obj.get_obname_only()
        else:
            _body += self.write_absent_attribute()


        return _body


class ToolLogicalRecord(EFLR):
    
    def __init__(self,
                 tools:list=None):

        super().__init__()

        if tools:
            self.tools = tools
        else:
            self.tools = []


        self.set_type = 'TOOL'

    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='TOOL', set_name=self.set_name).get_as_bytes()

        # TEMPLATE
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'DESCRIPTION')
        _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'TRADEMARK-NAME')
        _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'GENERIC-NAME')
        _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'PARTS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'STATUS')
        _body += write_struct('USHORT', get_representation_code('STATUS'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'CHANNELS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'PARAMETERS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        # VALUES
        for tool in self.tools:
            _body += tool.get_as_bytes()


        return self.finalize_bytes(5, _body)


# COMPLETE OBJREF
class Computation(EFLR):

    def __init__(self,
                 long_name:str=None,
                 properties:list=None,
                 dimension:list=None,
                 axis=None,
                 zones:list=None,
                 values:list=None,
                 representation_code:str=None,
                 units:str=None,
                 source=None):

        super().__init__()
        self.long_name = long_name
        if properties:
            self.properties = properties
        else:
            self.properties = []
        if dimension:
            self.dimension = dimension
        else:
            self.dimension = []
        self.axis = axis
        if zones:
            self.zones = zones
        else:
            self.zones = []
        if values:
            self.values = values
        else:
            self.values = []

        self.representation_code = representation_code
        self.units = units
        self.source = source

        self.set_type = 'COMPUTATION'

    def get_as_bytes(self):
        
        _body = b''

        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))

        if self.long_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.long_name)
        else:
            _body += self.write_absent_attribute()

        if self.properties:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.properties))
            for prop in self.properties:
                _body += write_struct('IDENT', prop)
        else:
            _body += self.write_absent_attribute()

        if self.dimension:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.dimension))
            for dim in self.dimension:
                _body += write_struct('UVARI', dim)
        else:
            _body += self.write_absent_attribute()

        if self.axis:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += self.axis.get_obname_only()
        else:
            _body += self.write_absent_attribute()

        if self.zones:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.zones))
            for zone in self.zones:
                _body += zone.get_obname_only()
        else:
            _body += self.write_absent_attribute()

        if self.values:
            if self.units:
                _body += write_struct('USHORT', int('00101111', 2))
                _body += write_struct('UVARI', len(self.zones))
                _body += write_struct('USHORT', get_representation_code(self.representation_code))
                _body += write_struct('UNITS', self.units)
            else:
                _body += write_struct('USHORT', int('00101101', 2))
                _body += write_struct('UVARI', len(self.zones))
                _body += write_struct('USHORT', get_representation_code(self.representation_code))
                
            for val in self.values:
                _body += write_struct(self.representation_code, val)
        else:
            _body += self.write_absent_attribute()

        if self.source:
            pass
        else:
            _body += self.write_absent_attribute()


        return _body


class ComputationLogicalRecord(EFLR):

    def __init__(self,
                 computations:list=None):

        super().__init__()
        if computations:
            self.computations = computations
        else:
            self.computations = []


        self.set_type = 'COMPUTATION'


    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='COMPUTATION', set_name=self.set_name).get_as_bytes()

        # long_name
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'LONG-NAME')
        _body += write_struct('USHORT', get_representation_code('ASCII'))

        # properties
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'PROPERTIES')
        _body += write_struct('USHORT', get_representation_code('IDENT'))

        # dimension
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'DIMENSION')
        _body += write_struct('USHORT', get_representation_code('UVARI'))

        # axis
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'AXIS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        # zones
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'ZONES')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        # values
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'VALUES')

        # source
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'SOURCE')


        # OBJECTS
        for computation in self.computations:
            _body += computation.get_as_bytes()


        return self.finalize_bytes(5, _body)


class Process(EFLR):

    def __init__(self,
                 description:str=None,
                 trademark_name:str=None,
                 version:str=None,
                 properties:list=None,
                 status:str=None,
                 input_channels:list=None,
                 output_channels:list=None,
                 input_computations:list=None,
                 output_computations:list=None,
                 parameters:list=None,
                 comments:str=None):

        super().__init__()

        self.description = description
        self.trademark_name = trademark_name
        self.version = version
        if properties:
            self.properties = properties
        else:
            self.properties = []
        self.status = status
        if input_channels:
            self.input_channels = input_channels
        else:
            self.input_channels = []
        if output_channels:
            self.output_channels = output_channels
        else:
            self.output_channels = []
        if input_computations:
            self.input_computations = input_computations
        else:
            self.input_computations = []
        if output_computations:
            self.output_computations = output_computations
        else:
            self.output_computations = []
        if parameters:
            self.parameters = parameters
        else:
            self.parameters = []
        self.comments = comments

        self.set_type = 'PROCESS'

    def get_as_bytes(self):

        _body = b''

        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        if self.description:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.description)
        else:
            _body += self.write_absent_attribute()
        
        if self.trademark_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.trademark_name)
        else:
            _body += self.write_absent_attribute()
        
        if self.version:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.version)
        else:
            _body += self.write_absent_attribute()
        
        if self.properties:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.properties))
            for prop in self.properties:
                _body += write_struct('IDENT', prop)
        else:
            _body += self.write_absent_attribute()
        
        if self.status:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.status)
        else:
            _body += self.write_absent_attribute()


        if self.input_channels:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.input_channels))
            for obj in self.input_channels:
                _body += obj.get_obname_only()

        if self.output_channels:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.output_channels))
            for obj in self.output_channels:
                _body += obj.get_obname_only()

        if self.input_computations:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.input_computations))
            for obj in self.input_computations:
                _body += obj.get_obname_only()

        if self.output_computations:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.output_computations))
            for obj in self.output_computations:
                _body += obj.get_obname_only()

        if self.parameters:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.parameters))
            for obj in self.parameters:
                _body += obj.get_obname_only()
        
        if self.comments:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.comments)
        else:
            _body += self.write_absent_attribute()



        return _body


class ProcessLogicalRecord(EFLR):

    def __init__(self,
                 processes:list=None):

        super().__init__()

        if processes:
            self.processes = processes
        else:
            self.processes = []


        self.set_type = 'PROCESS'

    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='PROCESS', set_name=self.set_name).get_as_bytes()

        # TEMPLATE
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'DESCRIPTION')
        _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'TRADEMARK-NAME')
        _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'VERSION')
        _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'PROPERTIES')
        _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'STATUS')
        _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'INPUT-CHANNELS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'OUTPUT-CHANNELS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'INPUT-COMPUTATIONS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'OUTPUT-COMPUTATIONS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'PARAMETERS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'COMMENTS')
        _body += write_struct('USHORT', get_representation_code('ASCII'))


        # OBJECTS

        for process in self.processes:
            _body += process.get_as_bytes()


        return self.finalize_bytes(5, _body)


class CalibrationMeasurement(EFLR):

    def __init__(self,
                 phase:str=None,
                 measurement_source=None,
                 _type:str=None,
                 dimension:list=None,
                 axis=None,
                 measurement:list=None,
                 measurement_representation_code:str=None,
                 measurement_units:str=None,
                 sample_count:list=None,
                 maximum_deviation:list=None,
                 standard_deviation:list=None,
                 begin_time=None,
                 duration=None,
                 duration_representation_code:str=None,
                 duration_units:str=None,
                 reference=None,
                 reference_representation_code:str=None,
                 reference_units:str=None,
                 standard=None,
                 standard_representation_code:str=None,
                 standard_units:str=None,
                 plus_tolerance:list=None,
                 minus_tolerance:list=None):

        super().__init__()
        self.phase = phase
        self.measurement_source = measurement_source
        self._type = _type
        
        if dimension:
            self.dimension = dimension
        else:
            self.dimension = []
        
        self.axis = axis
        
        if measurement:
            self.measurement = measurement
        else:
            self.measurement = []
        
        self.measurement_representation_code = measurement_representation_code
        self.measurement_units = measurement_units
        
        if sample_count:
            self.sample_count = sample_count
        else:
            self.sample_count = []
        
        if maximum_deviation:
            self.maximum_deviation = maximum_deviation
        else:
            self.maximum_deviation = []
        
        if standard_deviation:
            self.standard_deviation = standard_deviation
        else:
            self.standard_deviation = []
        
        self.begin_time = begin_time
        self.duration = duration
        self.duration_representation_code = duration_representation_code
        self.duration_units = duration_units
        self.reference = reference
        self.reference_representation_code = reference_representation_code
        self.reference_units = reference_units
        self.standard = standard
        self.standard_representation_code = standard_representation_code
        self.standard_units = standard_units
        
        if plus_tolerance:
            self.plus_tolerance = plus_tolerance
        else:
            self.plus_tolerance = []
        
        if minus_tolerance:
            self.minus_tolerance = minus_tolerance
        else:
            self.minus_tolerance = []


        self.set_type = 'CALIBRATION-MEASUREMENT'


    def get_as_bytes(self):

        _body = b''

        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))

        # VALUES

        if self.phase:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.phase)
        else:
            _body += self.write_absent_attribute()


        if self.measurement_source:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('OBJREF', self.measurement_source)
        else:
            _body += self.write_absent_attribute()


        if self._type:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self._type)
        else:
            _body += self.write_absent_attribute()


        if self.dimension:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.dimension))
            for dim in self.dimension:
                _body += write_struct('UVARI', dim)
        else:
            _body += self.write_absent_attribute()


        if self.axis:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('OBNAME', self.axis)
        else:
            _body += self.write_absent_attribute()


        if self.measurement:
            if self.measurement_units:
                _body += write_struct('USHORT', int('00101111', 2))
                _body += write_struct('UVARI', len(self.measurement))
                _body += write_struct('USHORT', get_representation_code(self.measurement_representation_code))
                _body += write_struct('UNITS', self.measurement_units)
            else:
                _body += write_struct('USHORT', int('00101101', 2))
                _body += write_struct('UVARI', len(self.measurement))
                _body += write_struct('USHORT', get_representation_code(self.measurement_representation_code))
             
            for val in self.measurement:
                _body += write_struct(self.measurement_representation_code, val)
        else:
            _body += self.write_absent_attribute()


        if self.sample_count:
            _body += write_struct('USHORT', int('00101101', 2))
            _body += write_struct('UVARI', len(self.sample_count))
            _body += write_struct('USHORT', get_representation_code('UVARI'))
            for val in self.sample_count:
                _body += write_struct('UVARI', val)
        else:
            _body += self.write_absent_attribute()


        if self.maximum_deviation:
            _body += write_struct('USHORT', int('00101101', 2))
            _body += write_struct('UVARI', len(self.maximum_deviation))
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
            for val in self.maximum_deviation:
                _body += write_struct('FDOUBL', val)
        else:
            _body += self.write_absent_attribute()


        if self.standard_deviation:
            _body += write_struct('USHORT', int('00101101', 2))
            _body += write_struct('UVARI', len(self.standard_deviation))
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
            for val in self.standard_deviation:
                _body += write_struct('FDOUBL', val)
        else:
            _body += self.write_absent_attribute()


        if self.begin_time:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('DTIME', self.begin_time)
        else:
            _body += self.write_absent_attribute()


        if self.duration:
            if self.duration_units:
                _body += write_struct('USHORT', int('00100111', 2))
                _body += write_struct('USHORT', get_representation_code(self.duration_representation_code))
                _body += write_struct('UNITS', self.duration_units)
            else:
                _body += write_struct('USHORT', int('00100101', 2))
                _body += write_struct('USHORT', get_representation_code(self.duration_representation_code))
             
            _body += write_struct(self.duration_representation_code, self.duration)
        else:
            _body += self.write_absent_attribute()


        if self.reference:
            if self.reference_units:
                _body += write_struct('USHORT', int('00101111', 2))
                _body += write_struct('UVARI', len(self.reference))
                _body += write_struct('USHORT', get_representation_code(self.reference_representation_code))
                _body += write_struct('UNITS', self.reference_units)
            else:
                _body += write_struct('USHORT', int('00101101', 2))
                _body += write_struct('UVARI', len(self.reference))
                _body += write_struct('USHORT', get_representation_code(self.reference_representation_code))
             
            for val in self.reference:
                _body += write_struct(self.reference_representation_code, val)
        else:
            _body += self.write_absent_attribute()


        if self.standard:
            if self.standard_units:
                _body += write_struct('USHORT', int('00101111', 2))
                _body += write_struct('UVARI', len(self.standard))
                _body += write_struct('USHORT', get_representation_code(self.standard_representation_code))
                _body += write_struct('UNITS', self.standard_units)
            else:
                _body += write_struct('USHORT', int('00101101', 2))
                _body += write_struct('UVARI', len(self.standard))
                _body += write_struct('USHORT', get_representation_code(self.standard_representation_code))
             
            for val in self.standard:
                _body += write_struct(self.standard_representation_code, val)
        else:
            _body += self.write_absent_attribute()


        if self.plus_tolerance:
            _body += write_struct('USHORT', int('00101101', 2))
            _body += write_struct('UVARI', len(self.plus_tolerance))
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
            for val in self.plus_tolerance:
                _body += write_struct('FDOUBL', val)
        else:
            _body += self.write_absent_attribute()


        if self.minus_tolerance:
            _body += write_struct('USHORT', int('00101101', 2))
            _body += write_struct('UVARI', len(self.minus_tolerance))
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
            for val in self.minus_tolerance:
                _body += write_struct('FDOUBL', val)
        else:
            _body += self.write_absent_attribute()


        return _body


class CalibrationMeasurementLogicalRecord(EFLR):

    def __init__(self,
                 calibration_measurements:list=None):

        super().__init__()

        if calibration_measurements:
            self.calibration_measurements = calibration_measurements
        else:
            self.calibration_measurements = []


        self.set_type = 'CALIBRATION-MEASUREMENT'


    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='CALIBRATION-MEASUREMENT', set_name=self.set_name).get_as_bytes()


        # TEMPLATE
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'PHASE')
        _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'MEASUREMENT-SOURCE')
        _body += write_struct('USHORT', get_representation_code('OBJREF'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'TYPE')
        _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'DIMENSION')
        _body += write_struct('USHORT', get_representation_code('UVARI'))
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'AXIS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'MEASUREMENT')
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'SAMPLE-COUNT')
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'MAXIMUM-DEVIATION')
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'STANDARD-DEVIATION')
        
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'BEGIN-TIME')
        _body += write_struct('USHORT', get_representation_code('DTIME'))
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'DURATION')
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'REFERENCE')
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'STANDARD')
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'PLUS-TOLERANCE')
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'MINUS-TOLERANCE')

        # OBJECTS
        for obj in self.calibration_measurements:
            _body += obj.get_as_bytes()


        return self.finalize_bytes(5, _body)


class CalibrationCoefficient(EFLR):

    def __init__(self,
                 label:str=None,
                 coefficients:list=None,
                 references:list=None,
                 plus_tolerances:list=None,
                 minus_tolerances:list=None):
        
        super().__init__()
        self.label = label
        if coefficients:
            self.coefficients = coefficients
        else:
            self.coefficients = []
        if references:
            self.references = references
        else:
            self.references = []
        if plus_tolerances:
            self.plus_tolerances = plus_tolerances
        else:
            self.plus_tolerances = []
        if minus_tolerances:
            self.minus_tolerances = minus_tolerances
        else:
            self.minus_tolerances = []



        self.set_type = 'CALIBRATION-COEFFICIENT'


    def get_as_bytes(self):

        _body = b''

        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))

        
        if self.label:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.label)
        else:
            _body += self.write_absent_attribute()
        
        if self.coefficients:
            _body += write_struct('USHORT', int('00101101', 2))
            _body += write_struct('UVARI', len(self.coefficients))
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
            for val in self.coefficients:
                _body += write_struct('FDOUBL', val)
        else:
            _body += self.write_absent_attribute()
        
        if self.references:
            _body += write_struct('USHORT', int('00101101', 2))
            _body += write_struct('UVARI', len(self.references))
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
            for val in self.references:
                _body += write_struct('FDOUBL', val)
        else:
            _body += self.write_absent_attribute()
        
        if self.plus_tolerances:
            _body += write_struct('USHORT', int('00101101', 2))
            _body += write_struct('UVARI', len(self.plus_tolerances))
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
            for val in self.plus_tolerances:
                _body += write_struct('FDOUBL', val)
        else:
            _body += self.write_absent_attribute()
        
        if self.minus_tolerances:
            _body += write_struct('USHORT', int('00101101', 2))
            _body += write_struct('UVARI', len(self.minus_tolerances))
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
            for val in self.minus_tolerances:
                _body += write_struct('FDOUBL', val)
        else:
            _body += self.write_absent_attribute()



        return _body


class CalibrationCoefficientLogicalRecord(EFLR):

    def __init__(self,
                 calibration_coefficients:list=None):

        super().__init__()

        if calibration_coefficients:
            self.calibration_coefficients = calibration_coefficients
        else:
            self.calibration_coefficients = []


        self.set_type = 'CALIBRATION-COEFFICIENT'

    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='CALIBRATION-COEFFICIENT', set_name=self.set_name).get_as_bytes()


        # TEMPLATE

        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'LABEL')
        _body += write_struct('USHORT', get_representation_code('IDENT'))

        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'COEFFICIENTS')

        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'REFERENCES')
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'PLUS-TOLERANCES')
        
        _body += write_struct('USHORT', int('00110000', 2))
        _body += write_struct('IDENT', 'MINUS-TOLERANCES')


        # OBJECTS

        for obj in self.calibration_coefficients:
            _body += obj.get_as_bytes()


        return self.finalize_bytes(5, _body)


class Calibration(EFLR):

    def __init__(self,
                 calibrated_channels:list=None,
                 uncalibrated_channels:list=None,
                 coefficients:list=None,
                 measurements:list=None,
                 parameters:list=None,
                 method:str=None):

        super().__init__()
        if calibrated_channels:
            self.calibrated_channels = calibrated_channels
        else:
            self.calibrated_channels = []

        if uncalibrated_channels:
            self.uncalibrated_channels = uncalibrated_channels
        else:
            self.uncalibrated_channels = []

        if coefficients:
            self.coefficients = coefficients
        else:
            self.coefficients = []

        if measurements:
            self.measurements = measurements
        else:
            self.measurements = []

        if parameters:
            self.parameters = parameters
        else:
            self.parameters = []

        self.method = method

        self.set_type = 'CALIBRATION'


    def get_as_bytes(self):

        _body = b''

        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        if self.calibrated_channels:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.calibrated_channels))
            for obj in self.calibrated_channels:
                _body += obj.get_obname_only()
        else:
            _body += self.write_absent_attribute()

        if self.uncalibrated_channels:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.uncalibrated_channels))
            for obj in self.uncalibrated_channels:
                _body += obj.get_obname_only()
        else:
            _body += self.write_absent_attribute()

        if self.coefficients:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.coefficients))
            for obj in self.coefficients:
                _body += obj.get_obname_only()
        else:
            _body += self.write_absent_attribute()

        if self.measurements:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.measurements))
            for obj in self.measurements:
                _body += obj.get_obname_only()
        else:
            _body += self.write_absent_attribute()

        if self.parameters:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.parameters))
            for obj in self.parameters:
                _body += obj.get_obname_only()
        else:
            _body += self.write_absent_attribute()

        if self.method:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.method)


        return _body


class CalibrationLogicalRecord(EFLR):

    def __init__(self,
                 calibrations:list=None):

        super().__init__()
        if calibrations:
            self.calibrations = calibrations
        else:
            self.calibrations = []


        self.set_type = 'CALIBRATION'


    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='CALIBRATION', set_name=self.set_name).get_as_bytes()

        # TEMPLATES
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'CALIBRATED-CHANNELS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'UNCALIBRATED-CHANNELS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'COEFFICIENTS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'MEASUREMENTS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'PARAMETERS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))

        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'METHOD')
        _body += write_struct('USHORT', get_representation_code('IDENT'))


        # OBJECTS

        for calibration in self.calibrations:
            _body += calibration.get_as_bytes()


        return self.finalize_bytes(5, _body)


class Group(EFLR):

    def __init__(self,
                 description:str=None,
                 object_type:str=None,
                 object_list:list=None,
                 group_list:list=None):

        super().__init__()

        self.description = description
        self.object_type = object_type
        
        if object_list:
            self.object_list = object_list
        else:
            self.object_list = []
        
        if group_list:
            self.group_list = group_list
        else:
            self.group_list = []

        self.set_type = 'GROUP'

    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(self.set_type, self.set_name).get_as_bytes()

        # TEMPLATE
        if self.description:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'DESCRIPTION')
            _body += write_struct('USHORT', get_representation_code('ASCII'))

        if self.object_type:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'OBJECT-TYPE')
            _body += write_struct('USHORT', get_representation_code('IDENT'))

        if self.object_list:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'OBJECT-LIST')
            _body += write_struct('USHORT', get_representation_code('OBNAME'))

        if self.group_list:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'GROUP-LIST')
            _body += write_struct('USHORT', get_representation_code('OBNAME'))


        # OBJ
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # ATTRIBUTES
        if self.description:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.description)

        if self.object_type:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.object_type)

        if self.object_list:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.object_list))
            for obj in self.object_list:
                _body += obj.get_obname_only()

        if self.group_list:
            _body += write_struct('USHORT', int('00101001', 2))
            _body += write_struct('UVARI', len(self.group_list))
            for obj in self.group_list:
                _body += obj.get_obname_only()


        return self.finalize_bytes(5, _body)






class EOD(object):
    def get_as_bytes(self, frame):
        


        _body = b''
        _body += frame.get_obname_only()
        _body += write_struct('USHORT', 0)

        _length = len(_body + 4)
        if _length % 2 == 0:
            _attributes = write_struct('USHORT', int('00000000', 2))
            _has_padding = False
        else:
            _attributes = write_struct('USHORT', int('00000001', 2))
            _length += 1
            _has_padding = True

        # HEADER

        _header = b''
        _header += write_struct('UNORM', _length)
        _header += _attributes
        _header += write_struct('USHORT', 127)

        _bytes = _header + _body

        if has_padding:
            _bytes += write_struct('USHORT', 0)


        return _bytes


