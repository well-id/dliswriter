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




class Equipment(object):

    def __init__(self,
                 set_name:str=None,
                 origin_reference:int=None,
                 copy_number:int=0,
                 object_name:str=None,
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
                 angular_drift_units:float=None,
                 has_padding:bool=False):

        self.set_name = set_name
        self.origin_reference = origin_reference
        self.copy_number = copy_number
        self.object_name = object_name
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

        self.has_padding = has_padding



    def get_as_bytes(self):

        # Body
        _body = b''

        # Set
        _body += Set(set_type='EQUIPMENT', set_name=self.set_name).get_as_bytes()

        # Template
        if self.trademark_name:
            print('Creating TM template')
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
            _body += write_struct('USHORT', 20)
            _body += write_struct('IDENT', self.trademark_name)

        if self.status:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 26)
            _body += write_struct('USHORT', int(self.status))

        if self._type:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 19)
            _body += write_struct('IDENT', self._type)

        if self.serial_number:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 19)
            _body += write_struct('IDENT', self.serial_number)

        if self.location:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 19)
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



        # HEADER
        if len(_body) % 2 != 0:
            self.has_padding = True
            _length = write_struct('UNORM', len(_body) + 5)
        else:
            _length = write_struct('UNORM', len(_body) + 4)

        _logical_record_type = write_struct('USHORT', 5)
        _attributes = write_struct('USHORT', int('1000000' + str(int(self.has_padding)), 2))

        _header = _length + _attributes + _logical_record_type


        _bytes = _header + _body
        if self.has_padding:
            _bytes += write_struct('USHORT', 1)

        return _bytes



class Axis(object):

    def __init__(self,
                 set_name:str=None,
                 origin_reference:int=None,
                 copy_number:int=0,
                 object_name:str=None,
                 axis_id:str=None,
                 coordinates:str=None,
                 spacing:str=None,
                 has_padding:bool=False):

        self.set_name = set_name
        self.origin_reference = origin_reference
        self.copy_number = copy_number
        self.object_name = object_name
        self.axis_id = axis_id
        self.coordinates = coordinates
        self.spacing = spacing
        self.has_padding = has_padding


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
            _body += write_struct('USHORT', 19)
            _body += write_struct('IDENT', self.axis_id)

        if self.coordinates:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 14)
            _body += write_struct('SLONG', self.coordinates)

        if self.spacing:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 14)
            _body += write_struct('SLONG', self.spacing)


        # HEADER
        if len(_body) % 2 != 0:
            self.has_padding = True
            _length = write_struct('UNORM', len(_body) + 5)
        else:
            _length = write_struct('UNORM', len(_body) + 4)

        _logical_record_type = write_struct('USHORT', 2)
        _attributes = write_struct('USHORT', int('1000000' + str(int(self.has_padding)), 2))

        _header = _length + _attributes + _logical_record_type


        _bytes = _header + _body
        if self.has_padding:
            _bytes += write_struct('USHORT', 1)

        return _bytes