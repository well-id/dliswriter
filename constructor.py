from datetime import datetime

from common.data_types import struct_type_dict
from common.data_types import write_struct

from utils.converters import get_logical_record_type
from utils.converters import get_representation_code

from storage_unit_label import StorageUnitLabel

from visible_record import VisibleRecord

from logical_record import LogicalRecordSegment
from logical_record import FileHeader
from logical_record import Equipment
from logical_record import Axis
from logical_record import ChannelLogicalRecord
from logical_record import Channel

from component import Set
from component import Attribute
from component import Template
from component import Object

from dlisio import dlis




# ----------------------- Create Storage Unit Label --------------------------------

sul = StorageUnitLabel()
sul.storage_unit_sequence_number = 1
sul.storage_set_identifier = 'Test Storage Unit'




# -------------------- Create File-Header --------------------------------


file_header = FileHeader()
file_header.sequence_number = 2
file_header._id = 'AQILAN TEST FILE-HEADER'
file_header.origin_reference = 41
file_header.name = 3




# -------------------- Create ORIGIN --------------------------------------

origin = LogicalRecordSegment()
origin.logical_record_type = get_logical_record_type('ORIGIN')
origin.has_predecessor_segment = False
origin.has_successor_segment = False

set_component = Set(set_type='ORIGIN')
set_component.set_name = 'DEFINING ORIGIN SET'
origin.set_component = set_component


origin_template = Template()



origin_template_attributes = [
    ('FILE-ID', 'ASCII'),
    ('FILE-SET-NAME', 'IDENT'),
    ('FILE-SET-NUMBER', 'UVARI'),
    ('FILE-NUMBER', 'UVARI'),
    ('FILE-TYPE', 'IDENT'),
    ('PRODUCT', 'ASCII'),
    ('VERSION', 'ASCII'),
    ('PROGRAMS', 'ASCII'),
    ('CREATION-TIME', 'DTIME'),
    ('ORDER-NUMBER', 'ASCII'),
    ('DESCENT-NUMBER', 'ASCII'),
    ('RUN-NUMBER', 'ASCII'),
    ('WELL-ID', 'ASCII'),
    ('WELL-NAME', 'ASCII'),
    ('FIELD-NAME', 'ASCII'),
    ('PRODUCER-CODE', 'UNORM'),
    ('PRODUCER-NAME', 'ASCII'),
    ('COMPANY', 'ASCII'),
    ('NAME-SPACE-NAME', 'IDENT'),
    ('NAME-SPACE-VERSION', 'UVARI')
]

for attribute_tuple in origin_template_attributes:
    attribute = Attribute()
    attribute.label = attribute_tuple[0]
    attribute.representation_code = attribute_tuple[1]

    origin_template.components.append(attribute)


origin.template = origin_template

origin_object = Object('DEFINING ORIGIN')
origin_object.origin_reference = 41

origin_object_attributes = [
    ('AQLN_TEST_FILE'),
    ('AQLN_FILEBATCH_FOR_TESTING'),
    (41),
    (170),
    ('PLAYBACK'),
    ('TEST PRODUCT'),
    ('0.0.1'),
    ('Sublime Text - Google Chrome'),
    (datetime.now()),
    ('89'),
    ('100'),
    ('2'),
    ('99'),
    ('AQILAN WELL 1'),
    ('ERDEK'),
    ('AQLN'),
    ('Omer Faruk Sari'),
    ('AQILAN'),
    ('AQILAN NAME SPACE'),
    ('15')
]

for attr in origin_object_attributes:
    attribute = Attribute()
    attribute.value = attr

    origin_object.attributes.append(attribute)

origin.objects.append(origin_object)



# EQUIPMENT
equipment = Equipment()
equipment.set_name = 'Equipment Set Name'
equipment.origin_reference = 41
equipment.copy_number = 0
equipment.object_name = 'SOME_EQPMNT'
equipment.trademark_name = 'EQ-TRADEMARKNAME'
equipment.serial_number = '9101-21391'
equipment.height = 140
equipment.height_units = 'in' 
equipment.length = 230.78
equipment.length_units = 'cm'
equipment.weight = 1.2
equipment.weight_units = 't'
equipment.pressure = 18000
equipment.pressure_units = 'psi'
equipment._type = 'Tool'


# AXIS
axis = Axis()
axis.set_name = 'AXIS SET NAME'
axis.origin_reference = 41
axis.object_name = 'AXISOBJNAME'
axis.axis_id = 31
axis.coordinates = 0
axis.spacing = 1





# CHANNELS

channel_logical_record = ChannelLogicalRecord()
channel_logical_record.set_type = 'CHANNEL'
channel_logical_record.set_name = 'CHANNL EFLR'


# Create a channel object
channel_1 = Channel()
channel_1.origin_reference = 41
channel_1.copy_number = 0
channel_1.object_name = 'DEPTH'

# Attributes
channel_1.long_name = 'DEPTH in mm'
channel_1.representation_code = 'SLONG'
channel_1.units = 'mm'
channel_1.dimension = [1]
channel_1.element_limit = [1]

# add to LR
channel_logical_record.channels.append(channel_1)


#  ADD another Channel
channel_2 = Channel()
channel_2.origin_reference = 41
channel_2.copy_number = 0
channel_2.object_name = 'WIDTH'

# Attributes
channel_2.long_name = 'WIDTH in mm'
channel_2.representation_code = 'SLONG'
channel_2.units = 'mm'
channel_2.dimension = [1]
channel_2.element_limit = [1]

# add to LR
channel_logical_record.channels.append(channel_2)













visible_record = VisibleRecord()
visible_record.logical_record_segments.append(file_header)
visible_record.logical_record_segments.append(origin)
visible_record.logical_record_segments.append(equipment)
visible_record.logical_record_segments.append(axis)
visible_record.logical_record_segments.append(channel_logical_record)


file_bytes = sul.get_as_bytes() + visible_record.get_as_bytes()

file_name = 'first_test.DLIS'
with open(file_name, 'wb') as f:
    f.write(file_bytes)


print(f'DLIS file {file_name} is created..')

print('Reading file with dlisio')
with dlis.load(file_name) as (f, *tail):
    print(f.describe())
    print('\n')
    print(f.fileheader.describe())
    print('\n')
    print(f.origins[0].describe())

print('\n\ndone..')