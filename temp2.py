from common.data_types import struct_type_dict
from common.data_types import read_struct
from common.data_types import write_struct

from utils.converters import get_logical_record_type
from utils.converters import get_representation_code

from storage_unit_label import StorageUnitLabel
from visible_record import VisibleRecord
from logical_record import LogicalRecordSegment

from component import Set
from component import Attribute
from component import Template
from component import Object

from datetime import datetime


# ----------------------- Create Storage Unit Label --------------------------------

sul = StorageUnitLabel()
sul.storage_unit_sequence_number = 1
sul.storage_set_identifier = 'Test Storage Unit'





# ------------------------ Create Visible Record -----------------------------------

visible_record = VisibleRecord()


# -------------------- Create File-Header --------------------------------

file_header = LogicalRecordSegment()

file_header.logical_record_type = get_logical_record_type('FILE-HEADER')
file_header.has_predecessor_segment = False # There is no Logical Record Segment BEFORE this one
file_header.has_successor_segment = True # There is a Logical Record Segment AFTER this one

set_component = Set(set_type='FILE-HEADER')
set_component.set_name = 'Test SET'

file_header.set_component = set_component

template = Template()

template_attribute_1 = Attribute()
template_attribute_1.label = 'SEQUENCE-NUMBER'
template_attribute_1.representation_code = get_representation_code('ASCII')

template.components.append(template_attribute_1)


template_attribute_2 = Attribute()
template_attribute_2.label = 'ID'
template_attribute_2.representation_code = get_representation_code('ASCII')

template.components.append(template_attribute_2)

file_header.template = template

# Objects
object_1 = Object('Default File Header')
object_1.origin_reference = 41


attribute_1 = Attribute()
attribute_1.value = 1
object_1.attributes.append(attribute_1)


attribute_2 = Attribute()
attribute_2.value = 'AQLN_TEST_FILE'
object_1.attributes.append(attribute_2)


file_header.objects.append(object_1)





# -------------------- Create ORIGIN --------------------------------------

origin = LogicalRecordSegment()
origin.logical_record_type = get_logical_record_type('ORIGIN')
origin.has_predecessor_segment = True
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
    attribute.representation_code = get_representation_code(attribute_tuple[1])

    origin_template.components.append(attribute)


origin.template = origin_template

origin_object = Object('DEFINING ORIGIN')
origin_object.origin_reference = 41

# Similarly, I will pass the values of the object attributes as a list.
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
    ('Ömer Faruk Sarı'),
    ('AQILAN'),
    ('AQILAN NAME SPACE'),
    ('15')
]

for attr in origin_object_attributes:
    attribute = Attribute()
    attribute.value = attr

    origin_object.attributes.append(attribute)

origin.objects.append(origin_object)