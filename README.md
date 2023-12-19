# DLIS Writer

Welcome to `dlis-writer`, possibly the only public Python library for creating DLIS files.

## Table of contents
- [Release log](#release-log)
- [About the DLIS format](#about-the-dlis-format)
- [User guide](#user-guide)
  - [Minimal example](#minimal-example)
  - [Extending basic metadata](#extending-basic-metadata)
  - [Adding more objects](#adding-more-objects)
  - [Example scripts](#example-scripts)
- [Developer guide](#developer-guide)
  - [More details about the format](#more-details-about-the-format)
  - [Storage Unit Label](#storage-unit-label)
  - [IFLR objects](#iflr-objects)
  - [EFLR objects](#eflr-objects)
    - [`EFLRSet` and `EFLRItem`](#eflrset-and-eflritem)
    - [Implemented EFLR objects](#implemented-eflr-objects)
    - [Relations between EFLR objects](#relations-between-eflr-objects)
  - [DLIS Attributes](#dlis-attributes)
    - [The `Attribute` class](#the-attribute-class)
    - [Attribute subtypes](#attribute-subtypes)
  

---
## Release log
TODO

---
## About the DLIS format
DLIS (Digital Log Information Standard) is a binary data format dedicated to storing well log data. 
It was developed in the 1980's, when data were stored on magnetic tapes.
Despite numerous advances in the field of information technology, DLIS is still prevalent in the oil and gas industry.

A DLIS file is composed of _logical records_ - topical units containing pieces of data and/or metadata. 
There are multiple subtypes of logical records which are predefined for specific types of (meta)data.
The most important ones are mentioned below, with links to more extensive descriptions 
in the [Developer guide](#developer-guide).

Every DLIS file starts with a logical record called [_Storage Unit Label (SUL)_](#storage-unit-label),
followed by a [_File Header_](#file-header). Both of these mainly contain format-specific metadata.

A file must also have at least one [_Origin_](#origin), which holds the key information 
about the scanned well, scan procedure, producer, etc.

Numerical data are kept in a [_Frame_](#frame), composed of several [_Channels_](#channel).
A channel can be interpreted as a single curve ('column' of data) or a single image (2D data).

Additional metadata can be specified using dedicated logical records subtypes, 
such as [Parameter](#parameter), [Zone](#zone), [Calibration](#calibration), [Equipment](#equipment), etc.
See [the list](#implemented-eflr-objects) for more details. 
Additionally, for possible relations between the different objects, 
see the relevant [class diagrams](#relations-between-eflr-objects).

---
## User guide
In the sections below you can learn how to define and write a DLIS file using the `dlis-writer`.

### Minimal example
Below you can see a very minimal DLIS file example with two 1D channels (one of which serves as the index)
and a single 2D channel.

```python
import numpy as np  # for creating mock datasets
from dlis_writer.file import DLISFile  # the main dlis-writer object you will interact with

# create a DLISFile object
# this also initialises StorageUnitLabel, FileHeader, and Origin with minimal default information
df = DLISFile()

# number of rows for creating the datasets
# all datasets (channels) belonging to the same frame must have the same number of rows
n_rows = 100

# define channels with numerical data and additional information
#  1) the first channel is also the index channel of the frame;
#     must be 1D, ideally should be monotonic and equally spaced
ch1 = df.add_channel('DEPTH', data=np.arange(n_rows) / 10, units='m')

#  2) second channel; in this case 1D and unitless
ch2 = df.add_channel("RPM", data=(np.arange(n_rows) % 10).astype(float))

#  3) third channel - an image channel (2D data)
ch3 = df.add_channel("AMPLITUDE", data=np.random.rand(n_rows, 5))

# define frame, referencing the above defined channels
main_frame = df.add_frame("MAIN FRAME", channels=(ch1, ch2, ch3), index_type='BOREHOLE-DEPTH')

# when all the required objects have been added, write the data and metadata to a physical DLIS file
df.write('./new_dlis_file.DLIS')

```

### Extending basic metadata
As mentioned above, initialising `DLISFile` object automatically constructs Storage Unit Label,
File Header, and Origin objects. However, the definition of each of these can be further tuned.

The relevant information can be passed either as a relevant pre-defined object or a dictionary
of key-word arguments to create one.

```python
from dlis_writer.file import DLISFile
from dlis_writer.logical_record.misc.storage_unit_label import StorageUnitLabel
from dlis_writer.logical_record.eflr_types.origin import OriginItem

# pre-defining Storage Unit Label as object
sul = StorageUnitLabel(set_identifier='MY-SET', sequence_number=5, max_record_length=4096)

# pre-defining File Header as dictionary
file_header = {'identifier': 'MY-FILE-HEADER', 'sequence_number': 5}

# pre-defining Origin as object
origin = OriginItem(
    'MY-ORIGIN',
    file_id='MY-FILE-ID',
    file_set_name='MY-FILE-SET-NAME',
    file_set_number=11,  # you should always define a file set number when defining OriginItem separately
    file_number=22,
    well_id=55,
    well_name='MY-WELL'
)

# defining DLISFile using the pre-defined objects/dictionaries
df = DLISFile(storage_unit_label=sul, file_header=file_header, origin=origin)
```

The attributes can also be changed later by accessing the relevant objects.
Note: because most attributes are instances of [`Attribute` class](#the-attribute-class),
you will need to use `.value` of the attribute you may want to change.

```python
origin.company.value = "COMPANY X"  # directly through the pre-defined Origin object
df.origin.producer_name.value = "PRODUCER Y"  # by accessing the Origin object through the DLISFile
```

### Adding more objects
Adding other logical records to the file is done in the same way as adding channels and frames.
For example, to add a zone (in depth or in time):

```python
zone1 = df.add_zone('DEPTH-ZONE', domain='BOREHOLE-DEPTH', minimum=2, maximum=4.5)
zone2 = df.add_zone('TIME-ZONE', domain='TIME', minimum=10, maximum=30)
```

To specify units for numerical values, use `.units` of the relevant attribute, e.g.
```python
zone1.minimum.units = 'in'  # inches  
zone2.maximum.units = 's'   # seconds
```

As per the [logical records relations graph](#relations-between-eflr-objects),
Zone objects can be used to define e.g. Splice objects (which also refer to Channels):

```python
splice1 = df.add_splice('SPLICE1', input_channels=(ch1, ch2), output_channel=ch3, zones=(zone1, zone2))
```

For more objects, see [the example with all kinds of objects](./examples/create_synth_dlis.py)
and [the description of all implemented objects](#implemented-eflr-objects).

Definition of all additional objects should precede the call to `.write()` of `DLISFile`, 
otherwise no strict order is observed.

### Example scripts
Scripts in the [examples](./examples) folder illustrate the basic usage of the library.

- [create_synth_dlis.py](./examples/create_synth_dlis.py) shows how to add every kind 
of DLIS object to the file - including Parameters, Equipment, Comments, No-Formats, etc.
It is also shown how multiple frames (in this case, a depth-based and a time-based frame) can be defined.

- [create_dlis_from_data.py](./examples/create_dlis_from_data.py) can be used to make a DLIS file
from any HDF5 data source.

- [create_synth_dlis_variable_data.py](./examples/create_synth_dlis_variable_data.py) allows creating DLIS files
with any number of 2D datasets with a user-defined shape, filled with randomised data. 

---
## Developer guide
TODO

### More details about the format
TODO; division: SUL, IFLR, EFLR; visible records vs logical records

### Storage Unit Label
TODO

### IFLR objects
TODO

### EFLR objects
TODO

#### `EFLRSet` and `EFLRItem`
TODO

#### Implemented EFLR objects
TODO

  ##### File Header
  TODO

  ##### Origin
  TODO

  ##### Channel
  TODO
  
  ##### Frame
  TODO

  ##### Axis
  TODO

  ##### Calibration Coefficient
  TODO

  ##### Calibration Measurement
  TODO

  ##### Calibration
  TODO

  ##### Computation
  TODO
  
  ##### Equipment
  TODO

  ##### Group
  TODO
  
  ##### Long Name
  TODO
  
  ##### Message
  TODO
  
  ##### Comment
  TODO

  ##### No-Format
  TODO
  
  ##### Parameter
  TODO
  
  ##### Path
  TODO

  ##### Process
  TODO

  ##### Splice
  TODO

  ##### Tool
  TODO

  ##### Well Reference Point
  TODO
  
  ##### Zone
  TODO

#### Relations between EFLR objects
Many of the EFLR objects are interrelated - e.g. a Frame refers to multiple Channels,
each of which can have an Axis; a Calibration uses Calibration Coefficients and Calibration Measurements;
a Tool has Equipments as parts. The relations are summarised in the diagram below.

```mermaid
---
title: EFLR objects relationships
---
classDiagram
    PathItem o-- "0..1" WellReferencePointItem
    PathItem o-- "0..*" ChannelItem
    PathItem o-- "0..1" FrameItem
    FrameItem o-- "0..*" ChannelItem
    CalibrationItem o-- "0..*" CalibrationCoefficientItem
    CalibrationItem o-- "0..*" CalibrationMeasurementItem
    CalibrationItem o-- "0..*" ChannelItem
    CalibrationItem o-- "0..*" ParameterItem
    CalibrationMeasurementItem o-- "0..1" ChannelItem
    CalibrationMeasurementItem o-- "0..1" AxisItem
    ComputationItem o-- "0..*" ZoneItem
    ComputationItem o-- "0..1" ToolItem
    ComputationItem o-- "0..1" AxisItem
    ParameterItem o-- "0..*" AxisItem
    ParameterItem o-- "0..*" ZoneItem
    SpliceItem o-- "0..*" ChannelItem
    SpliceItem o-- "0..*" ZoneItem
    ProcessItem o-- "0..*" ChannelItem
    ProcessItem o-- "0..*" ComputationItem
    ProcessItem o-- "0..*" ParameterItem
    ToolItem o-- "0..*" ChannelItem
    ToolItem o-- "0..*" ParameterItem
    ToolItem o-- "0..*" EquipmentItem
    ChannelItem o-- "0..*" AxisItem
    
    class AxisItem{
        +str axis_id
        +list coordinates
        +float spacing
    }
    
    class CalibrationItem{
        +list~ChannelItem~ calibrated_channels
        +list~ChannelItem~ uncalibrated_channels
        +list~CalibrationCoefficientItem~ coefficients
        +list~CalibrationMeasurementItem~ measurements
        +list~ParameterItem~ parameters
        +str method
    }
    
    class CalibrationMeasurementItem{
        +str phase
        +ChannelItem measurement_source
        +str _type
        +list~int~ dimension
        +AxisItem axis
        +list~float~ measurement
        +list~int~ sample_count
        +list~float~ maximum_deviation
        +list~float~ standard_deviation
        +datetime begin_time
        +float duration
        +list~int~ reference
        +list~float~ standard
        +list~float~ plus_tolerance
        +list~float~ minus_tolerance
    }
    
    class CalibrationCoefficientItem{
        +str label
        +list~float~ coefficients
        +list~float~ references
        +list~float~ plus_tolerances
        +list~float~ minus_tolerances
    }
    
    class ChannelItem{
        +str long_name
        +list~str~ properties
        +RepresentationCode representation_code
        +Units units
        +list~int~ dimension
        +list~AxisItem~ axis
        +list~int~ element_limit
        +str source
        +float minimum_value
        +float maximum_value
        +str dataset_name
    }
    
    class ComputationItem{
        +str long_name
        +list~str~ properties
        +list~int~ dimension
        +AxisItem axis
        +list~ZoneItem~ zones
        +list~float~ values
        +ToolItem source
    }
    
    class EquipmentItem{
        +str trademark_name
        +int status
        +str _type
        +str serial_number
        +str location
        +float height
        +float length
        +float minimum_diameter
        +float maximum_diameter
        +float volume
        +float weight
        +float hole_size
        +float pressure
        +float temperature
        +float vertical_depth
        +float radial_drift
        +float angular_drift
    }
    
    class FrameItem{
        +str description
        +list~ChannelItem~ channels
        +str index_type
        +str direction
        +float spacing
        +bool encrypted
        +int index_min
        +int index_max
    }
    
    
    class ParameterItem{
        +str long_name
        +list~int~ dimension
        +list~AxisItem~ axis
        +list~AxisItem~ zones
        +list values
    }
    
    class PathItem{
        +FrameItem frame_type
        +WellReferencePointItem well_reference_point
        +list~ChannelItem~ value
        +float borehole_depth
        +float vertical_depth
        +float radial_drift
        +float angular_drift
        +float time
        +float depth_offset
        +float measure_point_offset
        +float tool_zero_offset
    }
    
    class ProcessItem{
        +str description
        +str trademark_name
        +str version
        +list~str~ properties
        +str status
        +list~ChannelItem~ input_channels
        +list~ChannelItem~ output_channels
        +list~ComputationItem~ input_computations
        +list~ComputationItem~ output_computations
        +list~ParameterItem~ parameters
        +str comments
    }
    
    class SpliceItem{
        +list~ChannelItem~ output_channels
        +list~ChannelItem~ input_channels
        +list~ZoneItem~ zones
    }
    
    class ToolItem{
        +str description
        +str trademark_name
        +str generic_name
        +list~EquipmentItem~ parts
        +int status
        +list~ChannelItem~ channels
        +list~ParameterItem~ parameters
    }
    
    class WellReferencePointItem{
        +str permanent_datum
        +str vertical_zero
        +float permanent_datum_elevation
        +float above_permanent_datum
        +float magnetic_declination
        +str coordinate_1_name
        +float coordinate_1_value
        +str coordinate_2_name
        +float coordinate_2_value
        +str coordinate_3_name
        +float coordinate_3_value
    }
    
    class ZoneItem{
        +str description
        +str domain
        +float maximum
        +float minimum
    }
```

Other EFLR objects can be thought of as _standalone_ - they do not refer to other EFLR objects 
and are not explicitly referred to by any (althoug - as in case of NoFormat - a relation to IFLR objects can exist).

```mermaid
---
title: Standalone EFLR objects
---
classDiagram

    class MessageItem{
        +str _type
        +datetime time
        +float borehole_drift
        +float vertical_depth
        +float radial_drift
        +float angular_drift
        +float text
    }
    
    class CommentItem{
        +str: text
    }
    
    class LongNameItem{
        +str general_modifier
        +str quantity
        +str quantity_modifier
        +str altered_form
        +str entity
        +str entity_modifier
        +str entity_number
        +str entity_part
        +str entity_part_number
        +str generic_source
        +str source_part
        +str source_part_number
        +str conditions
        +str standard_symbol
        +str private_symbol
    }
    
    class NoFormatItem{
        +str consumer_name
        +str description
    }
    
    class OriginItem{
        +str file_id
        +str file_set_name
        +int file_set_number
        +int file_number
        +str file_type
        +str product
        +str version
        +str programs
        +datetime creation_time
        +int order_number
        +int descent_number
        +int run_number
        +int well_id
        +str well_name
        +str field_name
        +int producer_code
        +str producer_name
        +str company
        +str name_space_name
        +int name_space_version

    }
    
    class FileHeader{
        +str identifier
        +int sequence_number
    }
    
    
```

A special case is a Group object, which can refer to multiple other EFLR objects of a given type.
It can also keep references to other groups, creating a hierarchical structure.

```mermaid
---
title: EFLR Group object
---
classDiagram
    GroupItem o-- "0..*" EFLRItem
    GroupItem o-- "0..*" GroupItem

    class GroupItem{
        +str description
        +str object_type
        +list~EFLRItem~ object_list
        +list~GroupItem~ group_list
    }
    
```


### DLIS Attributes
TODO

#### The `Attribute` class
TODO

#### Attribute subtypes
TODO


------------------------------------------------

## FIRST STEPS

Every DLIS file must start with a Storage Unit Label and FileHeader.

### Storage Unit Label

Each DLIS file has to start with a Storage Unit Label (SUL) which is 80 bytes.
SUL has a specific format different from other Logical Record types.

Using the default is recommended.

*max_record_length* attribute determines the maximum length of each Visible Record.
This number is limited to **16384** and the default is **8192**.
Please check [related section on RP66 V1](http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_5) for details.


```python

from logical_record.storage_unit_label import StorageUnitLabel

sul = StorageUnitLabel()

```


### File Header

File Header must be exactly 124 bytes.

Recommended usage is to assign a max 65 characters *str* value to *_id* attribute, which represents the name of the logical file.

```python

from logical_record.file_header import FileHeader

file_header = FileHeader()
file_header.identifier = 'LOGICAL FILE NAME'

```




## Explicitly Formatted Logical Records (EFLR)

Majority of the [logical record types](http://w3.energistics.org/rp66/v1/rp66v1_appa.html#A_2) are categorized as EFLR.

This section aims to provide general information that will make things clear for the upcoming sections.

The usage of EFLR objects in this library is mostly the same.

Due to complicated requirements of the RP66V1 specification, the implementation might look non-intiuitive at first,
but it allows great control over each object and its attributes.


An EFLR class' attributes are instances of another class called Attribute. 

Each "Attribute" has:

1. label
2. count
3. representation_code
4. units
5. value

Most of the attributes of EFLR objects have default values, and for some of them user is expected to provide one or more of the
count, representation_code, units, value.

For an EFLR object, let's say origin, the usage of these attributes is shown below:

```
# Origin object has a file_id field as specified in the RP66V1.

origin.file_id # This is an instance of logical_record.utils.core.Attribute

origin.file_id.label # The label is pre-determined and SHOULD NOT BE CHANGED

origin.file_id.count # The number of values passed to this attribute

origin.file_id.representation_code # Data type of the value(s) passed

origin.file_id.units # The measurement unit of the passed value(s)

origin.file_id.value # A single value, or a list/tuple of values

```

Allowed types and limitations of these attributes for each EFLR can be found in logical_record.utils.rp66.RP66 object and
the explanation can be found in the next section.

### RP66 object

This object in logical_record.utils.rp66 serves as a dictionary for the entire library.

Each attribute of this object specifies the fields that can be used for each Set Type and
restrictions on count and representation code for each field.

For example file_id field of ORIGIN set looks like this:

```python
'file_id': {
    'count': 1,
    'representation_code': 'ASCII'
}
```

If count=1, then file_id.value can not contain more than 1 value (a list of values).
If count=None, then user is allowed to pass >=1 value(s) to field_id.value. For example:

```python
'programs': {
    'count': None,
    'representation_code': 'ASCII'
}
```

Here *programs* field of Origin set has a count=None. This means the user can pass more than 1 'ASCII' value using a list or tuple like this:

```python
origin.programs.value = ['PROGRAM 1', 'PROGRAM 2']
origin.programs.count = 2
```

If count and representation_code of a field has a value other than **None** user is **not allowed to change** count and representation_code
for that field.

If representation_code for of a field is None, then user **must provide a representation code** which denotes the data type of the value(s)
of that field.

A comprehensive example could be the AXIS set type for AXIS EFLR object.

This is the specification dictionary for AXIS in RP66 object.

```python
AXIS = {
    'axis_id': {
        'count': 1,
        'representation_code': 'IDENT'
    },
    'coordinates': {
        'count': None,
        'representation_code': None
    },
    'spacing': {
        'count': 1,
        'representation_code': None
    }
}
```

It shows that an Axis set have 3 fields:

1. axis_id
2. coordinates
3. spacing

The field *axis_id* has a count=1 and representation_code='IDENT'. This means user is allowed to pass only 1 value
and that value must be type of 'IDENT'.

```python
axis.axis_id.value = 'SOME TEXT'
```

As the count and representation_code is already specified for *axis_id* in the RP66, user should not change them.

The field *coordinates* have no count and representation_code so user **must provide** these. As there are no restrictions,
user is free to pass a list or tuple of values as long as all the values have the same data type (representation_code).
Below code demonstrates 2 different usages with 2 different representation codes:

```python


# VALUE PASSED AS LIST OF STRING
axis.coordinates.representation_code = 'ASCII'
axis.coordinates.count = 2
axis.coordinates.value = ["40 23' 42.8676'' N",
						  "27 47' 32.8956'' E"]



# VALUE PASSED AS LIST OF FLOAT
axis.coordinates.representation_code = 'FDOUBL'
axis.coordinates.count = 2
axis.coordinates.value = [40.395241, 27.792471]




```

The field *spacing* has a count of 1 and representation code will be provided by the user.
User is free to specify the units attribute of each field.
*units* might be useful for certain type of fields and *spacing* field of Axis set is a good example to this:

```python
axis.spacing.representation_code = 'FDOUBL'
axis.spacing.value = 0.33
axis.spacing.units = 'm'
```




### ORIGIN

Every DLIS file must contain at least one ORIGIN logical record and this is usually right after the SUL and FILE-HEADER.



```python

from logical_record.origin import Origin

origin = Origin('DEFINING ORIGIN')

origin.file_id.value = 'AQLN file_id'

origin.file_set_name.value = 'AQLN file_set_name'

origin.file_set_number.value = 11

origin.file_number.value = 22

origin.file_type.value = 'AQLN file_type'

origin.product.value = 'AQLN product'

origin.version.value = 'AQLN version'

origin.programs.value = 'AQLN programs'

origin.creation_time.value = datetime.now()

origin.order_number.value = 'AQLN order_number'

origin.descent_number.value = 33

origin.run_number.value = 44

origin.well_id.value = 55

origin.well_name.value = 'AQLN well_name'

origin.field_name.value = 'AQLN field_name'

origin.producer_code.value = 1

origin.producer_name.value = 'AQLN producer_name'

origin.company.value = 'AQLN company'

origin.name_space_name.value = 'AQLN name_space_name'

origin.name_space_version.value = 66

```


Please note that the *creation_time* field must be a datetime.datetime instance.

```python

from datetime import datetime

now = datetime_now()

origin.creation_time.value = now

```


### WELL REFERENCE POINT

Here we did not use *coordinate_3_name* and *coordinate_3_value* fields.

```python

from logical_record.well_reference_point import WellReferencePoint

well_reference_point = WellReferencePoint('AQLN WELL-REF')

well_reference_point.permanent_datum.value = 'AQLN permanent_datu'

well_reference_point.vertical_zero.value = 'AQLN vertical_zero'

well_reference_point.permanent_datum_elevation.value = 1234.51

well_reference_point.above_permanent_datum.value = 888.51

well_reference_point.magnetic_declination.value = 999.51

well_reference_point.coordinate_1_name.value = 'Lattitude'

well_reference_point.coordinate_1_value.value = 40.395240

well_reference_point.coordinate_2_name.value = 'Longitude'

well_reference_point.coordinate_2_value.value = 27.792470

```

### AXIS

```python

from logical_record.axis import Axis

axis = Axis('AXS-1')

axis.axis_id.value = 'FIRST AXIS'

axis.coordinates.representation_code = 'FDOUBL'
axis.coordinates.count = 2
axis.coordinates.value = [40.395241, 27.792471]

axis.spacing.representation_code = 'FDOUBL'
axis.spacing.value = 0.33
axis.spacing.units = 'm'

```

### LONG NAME

```python

from logical_record.long_name import LongName

long_name = LongName('LNAME-1')

long_name.general_modifier.value = 'SOME ASCII TEXT'

long_name.quantity.value = 'SOME ASCII TEXT'

long_name.quantity_modifier.value = 'SOME ASCII TEXT'

long_name.altered_form.value = 'SOME ASCII TEXT'

long_name.entity.value = 'SOME ASCII TEXT'

long_name.entity_modifier.value = 'SOME ASCII TEXT'

long_name.entity_number.value = 'SOME ASCII TEXT'

long_name.entity_part.value = 'SOME ASCII TEXT'

long_name.entity_part_number.value = 'SOME ASCII TEXT'

long_name.generic_source.value = 'SOME ASCII TEXT'

long_name.source_part.value = 'SOME ASCII TEXT'

long_name.source_part_number.value = 'SOME ASCII TEXT'

long_name.conditions.value = 'SOME ASCII TEXT'

long_name.standard_symbol.value = 'SOME ASCII TEXT'

long_name.private_symbol.value = 'SOME ASCII TEXT'

```


### CHANNEL


You can think of Channel as a column.

For example let's say in your dataset, you have a column
called DEPTH, the values are float, the unit is meter, and each cell contains a single value so the dimension
is 1. This is how you would create the Channel for DEPTH column.

```python

from logical_record.channel import Channel

depth_channel = Channel('DEPTH CHANNEL')
depth_channel.long_name.value = 'DEPTH'
depth_channel.properties.value = ['0309 AQLN PROP 1', 'PROP AQLN 2']
depth_channel.representation_code.value = get_representation_code('FDOUBL')
depth_channel.units.value = 'm'
depth_channel.dimension.value = [1]
depth_channel.element_limit.value = [1]

```

*data.csv* has two more columns, we create channels for those as well.

```python

from logical_record.channel import Channel

curve_1_channel = Channel('CURVE 1 CHANNEL')
curve_1_channel.long_name.value = 'CURVE 1'
curve_1_channel.representation_code.value = get_representation_code('FDOUBL')
curve_1_channel.units.value = 't'
curve_1_channel.dimension.value = [1]
curve_1_channel.element_limit.value = [1]

curve_2_channel = Channel('CURVE 2 CHANNEL')
curve_2_channel.long_name.value = 'CURVE 2'
curve_2_channel.representation_code.value = get_representation_code('FDOUBL')
curve_2_channel.units.value = 't'
curve_2_channel.dimension.value = [1]
curve_2_channel.element_limit.value = [1]

```

For multi-dimensional columns, you must specify the dimension field's value accordingly.
Dimension attributes denotes the dimension of the array in a single cell.
For example the *image.csv* file has dimensions (7657, 384). This means,
there are 7657 rows, each containing 384 values. So the dimension will be 384 as
it denotes the dimension of each value in a single cell.


```python

from logical_record.channel import Channel

image_channel = Channel('IMG')
image_channel.long_name.value = 'IMAGE CHANNEL'
image_channel.representation_code.value = get_representation_code('FDOUBL')
image_channel.dimension.value = [384]
image_channel.element_limit.value = [384]

```



### FRAME & FRAME DATA

Each frame can have a varied number of Channel instances.
Frames can be thought as separate spreadsheets with different combinations of Channels (columns)

For each Frame, user must first create a Frame(EFLR) object and afterwards for each row of each column (Channel)
create a Frame Data.


Creating the Frame(EFLR)

```python

from logical_record.frame import Frame

frame = Frame('MAIN')
frame.channels.value = [depth_channel, curve_1_channel, curve_2_channel, image_channel]
frame.index_type.value = 'BOREHOLE-DEPTH'
frame.spacing.value = 0.33
frame.spacing.representation_code = 'FDOUBL'
frame.spacing.units = 'm'

```

Reading data:

```python

import pandas as pd

data = pd.read_csv('./data/data.csv')
image = pd.read_csv('./data/image.csv', header=None, sep=' ')

# Remove index col if exists 
data = data[[col for col in data.columns[1:]]]

# Convert to numpy.ndarray
data = data.values
image = image.values

```

Each FrameData object represents a single row. FrameData must follow the Frame object and the order of the data passed should be the same with
the order of the Channels in Frame.channels.value field.

For this example *frame* is an instance of Frame(EFLR) and has 2 channels: depth_channel and image_channel.

Each frame data should contain depth_channel values followed by image_channel. The data passed to FrameData
must be a 1 dimensional np.array or a list.

In this example the *depth_channel*, *curve_1_channel*, and *curve_2_channel* are instances of Channel (created previously) and all have a dimension of 1.

*image_channel* on the other hand, has a dimension of 384. So, data that will be passed to each FrameData object
must be a list of 387 values, first three being the values of *depth_channel*, *curve_1_channel*, and *curve_2_channel* in the same row.
Following 384 values are the *image_channel* values for the corresponding row.

This example uses numpy's append method to manipulate the datasets to get the list of values passed to FrameData objects.

```python

from logical_record.frame_data import FrameData

frame_data_objects = []

for i in range(len(data)):

    slots = np.append(data[i], image[i])

    frame_data = FrameData(frame=frame, frame_number=i+1, slots=slots)
    frame_data_objects.append(frame_data)

``` 

Please note that, reading & manipulating datasets might differ depending on the format of the data files.

User is expected to create an array for each row and pass that array to FrameData object.



### PATH

*frame_type* must be an instance of a Frame(EFLR) object.
*well_reference_point* must be an instance of a WellReferencePoint(EFLR) object.
*value* must be a list of Channel instances.

```python

from logical_record.path import Path

path_1 = Path('PATH1')

path_1.frame_type.value = frame
path_1.well_reference_point.value = well_reference_point
path_1.value.value = [curve_1_channel, curve_2_channel]

path_1.vertical_depth.value = -187
path_1.vertical_depth.representation_code = 'SNORM'

path_1.radial_drift.value = 105
path_1.radial_drift.representation_code = 'SSHORT'

path_1.angular_drift.value = 64.23
path_1.angular_drift.representation_code = 'FDOUBL'

path_1.time.value = 180
path_1.time.representation_code = 'SNORM'

path_1.depth_offset.value = -123
path_1.depth_offset.representation_code = 'SSHORT'

path_1.measure_point_offset.value = 82
path_1.measure_point_offset.representation_code = 'SSHORT'

path_1.tool_zero_offset.value = -7
path_1.tool_zero_offset.representation_code = 'SSHORT'

```


### ZONE

> [Zone Objects](http://w3.energistics.org/rp66/v1/rp66v1_sec5.html#5_8_1) specify single intervals in depth or time.

Domain attribute can be:

1. BOREHOLE-DEPTH
2. TIME
3. VERTICAL-DEPTH

Maximum and Minimum attributes' representation code will depend on the domain attribute.

A comprehensive example showing 4 different usage of this object:

```python

from datetime import datetime
from logical_record.zone import Zone

# Domain = BOREHOLE-DEPTH
zone_1 = Zone('ZONE-1')
zone_1.description.value = 'BOREHOLE-DEPTH-ZONE'
zone_1.domain.value = 'BOREHOLE-DEPTH'

zone_1.maximum.value = 1300.45
zone_1.maximum.units = 'm'
zone_1.maximum.representation_code = 'FDOUBL'

zone_1.minimum.value = 100
zone_1.minimum.units = 'm'
zone_1.minimum.representation_code = 'USHORT'


# Domain = VERTICAL-DEPTH
zone_2 = Zone('ZONE-2')
zone_2.description.value = 'VERTICAL-DEPTH-ZONE'
zone_2.domain.value = 'VERTICAL-DEPTH'

zone_2.maximum.value = 2300.45
zone_2.maximum.units = 'm'
zone_2.maximum.representation_code = 'FDOUBL'

zone_2.minimum.value = 200
zone_2.minimum.units = 'm'
zone_2.minimum.representation_code = 'USHORT'


# Domain = TIME and values are passed as datetime.datetime instances
zone_3 = Zone('ZONE-3')
zone_3.description.value = 'ZONE-TIME'
zone_3.domain.value = 'TIME'

zone_3.maximum.value = datetime(2022, 7, 13, 11, 30)
zone_3.maximum.representation_code = 'DTIME'

zone_3.minimum.value = datetime(2022, 7, 12, 9, 0)
zone_3.minimum.representation_code = 'DTIME'

# Domain = TIME and values are passed as integers denoting n minutes since something.
zone_4 = Zone('ZONE-4')
zone_4.description.value = 'ZONE-TIME-2'
zone_4.domain.value = 'TIME'

zone_4.maximum.value = 90
zone_4.maximum.units = 'minute'
zone_4.maximum.representation_code = 'USHORT'

zone_4.minimum.value = 10
zone_4.minimum.units = 'minute'
zone_4.minimum.representation_code = 'USHORT'

```

### PARAMETER

Example usage

```python

from logical_record.parameter import Parameter

parameter_1 = Parameter('PARAM-1')

parameter_1.long_name.value = 'LATLONG-GPS'

parameter_1.dimension.value = [1]

parameter_1.zones.value = [zone_1, zone_3]

parameter_1.values.value = ["40deg 23' 42.8676'' N", "40deg 23' 42.8676'' N"]
parameter_1.values.representation_code = 'ASCII'

```


### EQUIPMENT

Please note that even though RP66 V1 does not restrict the representation code for the attributes listed below, to make it easier for the user
their default representation codes are set to FDOUBL. This object is an exception where you can set the representation codes even though they are not None in the logical_record.utils.rp66.RP66.

- height
- length
- minimum_diameter
- maximum_diameter
- volume
- weight
- hole_size
- pressure
- temperature
- vertical_depth
- radial_drift
- angular_drift


```python

from logical_record.equipment import Equipment

equipment = Equipment('EQ1')
equipment.trademark_name.value = 'EQ-TRADEMARKNAME'
equipment.status.value = 1
equipment._type.value = 'Tool'
equipment.serial_number.value = '9101-21391'
equipment.location.value = 'Well'

equipment.height.value = 140
equipment.height.units = 'in' 

equipment.length.value = 230.78
equipment.length.units = 'cm'

equipment.minimum_diameter.value = 2.3
equipment.minimum_diameter.units = 'm'

equipment.maximum_diameter.value = 3.2
equipment.maximum_diameter.units = 'm'

equipment.volume.value = 100
equipment.volume.units = 'cm3'

equipment.weight.value = 1.2
equipment.weight.units = 't'

equipment.hole_size.value = 323.2
equipment.hole_size.units = 'm' 

equipment.pressure.value = 18000
equipment.pressure.units = 'psi' 

equipment.temperature.value = 24
equipment.temperature.units = 'degC' 

equipment.vertical_depth.value = 587
equipment.vertical_depth.units = 'm'

equipment.radial_drift.value = 23.22
equipment.radial_drift.units = 'm' 

equipment.angular_drift.value = 32.5
equipment.angular_drift.units = 'm'

```


### TOOL

*parts* attribute is a list of Equipment object instances.
*channels* attribute is a list of Channel objects.
*parameters* attribute is a list of Parameter objects.


```python

from logical_record.tool import Tool

tool = Tool('TOOL-1')
tool.description.value = 'SOME TOOL'
tool.trademark_name.value = 'SMTL'
tool.generic_name.value = 'TOOL GEN NAME'
tool.parts.value = [equipment_1, equipment_2]
tool.status.value = 1
tool.channels.value = [depth_channel, curve_1_channel]
tool.parameters.value = [parameter_1, parameter_3]

```


### COMPUTATION

*axis* attribute must be an Axis object

*zones* attribute must be a list of Zone objects

*values* attribute must contain a list of values. Note that the number of values MUST BE THE SAME with number of Zone objects in the *zones* attribute.
Representation code of *values* must be specified.

*source* attribute can be a reference to another object that is the direct source of this computation.
There are two representation codes that can be used for referencing an object: 'OBNAME' and 'OBJREF'.
Below example assigns a Tool object created before as the *source* and sets the representation code to 'OBNAME'.


```python

from logical_record.computation import Computation

computation = Computation('COMPT-1')

computation.long_name.value = 'COMPT 1'

computation.properties.value = ['PROP 1', 'AVERAGED']

computation.dimension.value = [1]

computation.axis.value = axis

computation.zones.value = [zone_1, zone_2, zone_3]

computation.values.value = [100, 200, 300]
computation.values.representation_code = 'UNORM'

computation.source.value = tool
computation.source.representation_code = 'OBNAME'

```


### PROCESS

*status* attribute can take 3 values:

1. COMPLETE
2. ABORTED
3. IN-PROGRESS

*input_channels*, *output_channels*, *input_computations*, *output_computations*, and *parameters* attributes are list of related object instances.

```python

from logical_record.process import Process

process_1 = Process('MERGED')

process_1.description.value = 'MERGED'

process_1.trademark_name.value = 'PROCESS 1'

process_1.version.value = '0.0.1'

process_1.properties.value = ['AVERAGED']

process_1.status.value = 'COMPLETE'

process_1.input_channels.value = [curve_1_channel]

process_1.output_channels.value = [multi_dim_channel]

process_1.input_computations.value = [computation_1]

process_1.output_computations.value = [computation_2]

process_1.parameters.value = [parameter_1, parameter_2, parameter_3]

process_1.comments.value = 'SOME COMMENT HERE'

```


### CALIBRATION MEASUREMENT

```python
from logical_record.calibration import CalibrationMeasurement

calibration_measurement_1 = CalibrationMeasurement('CMEASURE-1')

calibration_measurement_1.phase.value = 'BEFORE'

calibration_measurement_1.measurement_source.value = depth_channel

calibration_measurement_1._type.value = 'Plus'

calibration_measurement_1.dimension.value = [1]

calibration_measurement_1.measurement.value = [12.2323]
calibration_measurement_1.measurement.representation_code = 'FDOUBL'

calibration_measurement_1.sample_count.value = [12]
calibration_measurement_1.sample_count.representation_code = 'USHORT'

calibration_measurement_1.maximum_deviation.value = [2.2324]
calibration_measurement_1.maximum_deviation.representation_code = 'FDOUBL'

calibration_measurement_1.standard_deviation.value = [1.123]
calibration_measurement_1.standard_deviation.representation_code = 'FDOUBL'

calibration_measurement_1.begin_time.value = datetime.now()
calibration_measurement_1.begin_time.representation_code = 'DTIME'

calibration_measurement_1.duration.value = 15
calibration_measurement_1.duration.representation_code = 'USHORT'
calibration_measurement_1.duration.units = 's'

calibration_measurement_1.reference.value = [11]
calibration_measurement_1.reference.representation_code = 'USHORT'

calibration_measurement_1.standard.value = [11.2]
calibration_measurement_1.standard.representation_code = 'FDOUBL'

calibration_measurement_1.plus_tolerance.value = [2]
calibration_measurement_1.plus_tolerance.representation_code = 'USHORT'

calibration_measurement_1.minus_tolerance.value = [1]
calibration_measurement_1.minus_tolerance.representation_code = 'USHORT'
```


### CALIBRATION COEFFICIENT


```python
from logical_record.calibration import CalibrationCoefficient

calibration_coefficient = CalibrationCoefficient('COEF-1')

calibration_coefficient.label.value = 'Gain'

calibration_coefficient.coefficients.value = [100.2, 201.3]
calibration_coefficient.coefficients.representation_code = 'FDOUBL'

calibration_coefficient.references.value = [89, 298]
calibration_coefficient.references.representation_code = 'FDOUBL'

calibration_coefficient.plus_tolerances.value = [100.2, 222.124]
calibration_coefficient.plus_tolerances.representation_code = 'FDOUBL'

calibration_coefficient.minus_tolerances.value = [87.23, 214]
calibration_coefficient.minus_tolerances.representation_code = 'FDOUBL'
```


### CALIBRATION

```python
from logical_record.calibration import Calibration

calibration = Calibration('CALB-MAIN')

calibration.calibrated_channels.value = [depth_channel, curve_1_channel]

calibration.uncalibrated_channels.value = [curve_2_channel, multi_dim_channel, image_channel]

calibration.coefficients.value = [calibration_coefficient]

calibration.measurements.value = [calibration_measurement_1]

calibration.parameters.value = [parameter_1, parameter_2, parameter_3]

calibration.method.value = 'Two-Point-Linear'
```


### GROUP

```python
from logical_record.group import Group

group_1 = Group('GRP-1')

group_1.description.value = 'MULTI-DIMENSIONAL CHANNELS'
group_1.item_type.value = 'CHANNEL'
group_1.object_list.value = [multi_dim_channel, image_channel]

```


### SPLICE
```python
from logical_record.splice import Splice

splice_1 = Splice('SPLICE-1')
splice_1.output_channels.value = multi_dim_channel
splice_1.input_channels.value = [curve_1_channel, curve_2_channel]
splice_1.zones.value = [zone_1, zone_2, zone_3, zone_4]

```


### NO-FORMAT EFLR & FRAME DATA

NO-FORMAT Logical Records allow users to write arbitrary bytes data.

There are 2 steps:

1. Creating NoFormat(EFLR) objects
2. Creatinf NOFORMAT Frame Data that points to a NoFormat(EFLR) object


#### NoFormat (EFLR)

This object can be thought of a parent class for the NoFormat FrameData(s).
This example creates two NoFormat objects:


```python
from logical_record.no_format import NoFormat

no_format_1 = NoFormat('no_format_1')
no_format_1.consumer_name.value = 'SOME TEXT NOT FORMATTED'
no_format_1.description.value = 'TESTING-NO-FORMAT'

no_format_2 = NoFormat('no_format_2')
no_format_2.consumer_name.value = 'SOME IMAGE NOT FORMATTED'
no_format_2.description.value = 'TESTING-NO-FORMAT-2'

```

#### NOFORMAT FRAME DATA (IFLR)

NOFORMAT FrameData only has two attributes:

1. no_format_object: A logical_record.no_format.NoFormat instance
2. data: a binary data


An arbitrary number of NOFORMAT FrameData can be created.

This example creates three NOFORMAT FrameData, two of them points to no_format_1,
and one of them to no_format_2 objects that were created in the previous step.

```python
from logical_record.frame_data import FrameData

no_format_fdata_1 = NoFormatFrameData()
no_format_fdata_1.no_format_object = no_format_1
no_format_fdata_1.image1 = 'Some text that is recorded but never read by anyone.'

no_format_fdata_2 = NoFormatFrameData()
no_format_fdata_2.no_format_object = no_format_1
no_format_fdata_2.image1 = 'Some OTHER text that is recorded but never read by anyone.'

no_format_fdata_3 = NoFormatFrameData()
no_format_fdata_3.no_format_object = no_format_2
no_format_fdata_3.image1 = 'This could be the BINARY data of an image rather than ascii text'

```

#### COMPLETE CODE

```python
from logical_record.no_format import NoFormat
from logical_record.frame_data import NoFormatFrameData

no_format_1 = NoFormat('no_format_1')
no_format_1.consumer_name.value = 'SOME TEXT NOT FORMATTED'
no_format_1.description.value = 'TESTING-NO-FORMAT'

no_format_2 = NoFormat('no_format_2')
no_format_2.consumer_name.value = 'SOME IMAGE NOT FORMATTED'
no_format_2.description.value = 'TESTING-NO-FORMAT-2'

no_format_fdata_1 = NoFormatFrameData()
no_format_fdata_1.no_format_object = no_format_1
no_format_fdata_1.data = 'Some text that is recorded but never read by anyone.'

no_format_fdata_2 = NoFormatFrameData()
no_format_fdata_2.no_format_object = no_format_1
no_format_fdata_2.data = 'Some OTHER text that is recorded but never read by anyone.'

no_format_fdata_3 = NoFormatFrameData()
no_format_fdata_3.no_format_object = no_format_2
no_format_fdata_3.data = 'This could be the BINARY data of an image rather than ascii text'

```


### MESSAGE

*time* attribute can be passed as a datetime.datetime instance or as a numeric value that denotes
x min/sec/hour/ since something.

```python
from logical_record.message import Message

message_1 = Message('MESSAGE-1')
message_1._type.value = 'Command'

message_1.time.value = datetime.now()
message_1.time.representation_code = 'DTIME'

message_1.borehole_drift.value = 123.34
message_1.borehole_drift.representation_code = 'FDOUBL'

message_1.vertical_depth.value = 234.45
message_1.vertical_depth.representation_code = 'FDOUBL'

message_1.radial_drift.value = 345.56
message_1.radial_drift.representation_code = 'FDOUBL'

message_1.angular_drift.value = 456.67
message_1.angular_drift.representation_code = 'FDOUBL'

message_1.text.value = 'Test message 11111'

```


### COMMENT

```python
from logical_record.message import Comment

comment_1 = Comment('COMMENT-1')
comment_1.text.value = 'SOME COMMENT HERE'

comment_2 = Comment('COMMENT-2')
comment_2.text.value = 'SOME OTHER COMMENT HERE'

```


### CREATING DLIS FILE

First step is to create a DLISFile object.

Each DLIS File must have a Storage Unit Label, File Header and an Origin.
All other Logical Records must have an attribute *origin_reference* that points to the
related Origin object's *file_set_number*. So, rather than setting some_logical_record.origin_reference
each time user creates a Logical Record, the Origin object is passed to __init__ of the DLISFile
and *origin_reference*s of all Logical Records are set internally.

*file_path*: The path of the DLIS file that will be written to.
*storage_unit_label*: A logical_record.storage_unit_label.StorageUnitLabel instance.
*file_header*: A logical_record.file_header.FileHeader instance.
*origin*: A logical_record.origin.Origin instance.

Below example uses the same variable names used in previous steps to create each Logical Record Segment.

For example *sul* is the name that we used when creating the StorageUnitLabel object.

```python
from logical_record.file import DLISFile

dlis_file = DLISFile(file_path='./output/test.DLIS',
                     storage_unit_label=sul,
                     file_header=file_header,
                     origin=origin)
```

Next step is to append all the Logical Record Segments created in previous segments.
This is done by appending the related object instances to *logical_records* attribute of the DLISFile object.


```python

dlis_file.logical_records.append(well_reference_point)
dlis_file.logical_records.append(axis)
dlis_file.logical_records.append(long_name)
dlis_file.logical_records.append(depth_channel)
dlis_file.logical_records.append(curve_1_channel)
dlis_file.logical_records.append(curve_2_channel)
dlis_file.logical_records.append(multi_dim_channel)
dlis_file.logical_records.append(image_channel)

dlis_file.logical_records.append(frame)
for fdata in frame_data_objects:
    dlis_file.logical_records.append(fdata)

dlis_file.logical_records.append(path_1)
dlis_file.logical_records.append(zone_1)
dlis_file.logical_records.append(zone_2)
dlis_file.logical_records.append(zone_3)
dlis_file.logical_records.append(zone_4)
dlis_file.logical_records.append(parameter_1)
dlis_file.logical_records.append(parameter_2)
dlis_file.logical_records.append(parameter_3)
dlis_file.logical_records.append(equipment_1)
dlis_file.logical_records.append(equipment_2)
dlis_file.logical_records.append(tool)
dlis_file.logical_records.append(computation_1)
dlis_file.logical_records.append(computation_2)
dlis_file.logical_records.append(process_1)
dlis_file.logical_records.append(process_2)
dlis_file.logical_records.append(calibration_measurement_1)
dlis_file.logical_records.append(calibration_coefficient)
dlis_file.logical_records.append(calibration)
dlis_file.logical_records.append(group_1)
dlis_file.logical_records.append(splice_1)
dlis_file.logical_records.append(no_format_1)
dlis_file.logical_records.append(no_format_2)
dlis_file.logical_records.append(no_format_fdata_1)
dlis_file.logical_records.append(no_format_fdata_2)
dlis_file.logical_records.append(no_format_fdata_3)
dlis_file.logical_records.append(message_1)
dlis_file.logical_records.append(comment_1)
dlis_file.logical_records.append(comment_2)

```

Adding all the logical records at the last step was an arbitrary decision made for demonstration purposes.

A more intuitive way might be:

1. Create StorageUnitLabel
2. Create FileHeader
3. Create Origin
4. Create DLISFile
5. Create other Logical Records and append them to DLISFile().logical_records on the fly

A basic demonstration of this approach:

```python
... imports
..
.

sul = StorageUnitLabel()
file_header = FileHeader()
origin = Origin()
... origin attributes
..
.

dlis_file = DLISFile(file_path='some_path.DLIS', sul, file_header, origin)


well_reference_point = WellReferencePoint()
... well_reference_point attributes
..
.

dlis_file.logical_records.append(well_reference_point)


channel = Channel()
... channel attributes
..
.

dlis_file.logical_records.append(channel)
```


## DLIS objects
```mermaid
---
title: Logical record types overview
---
classDiagram
    LogicalRecordBase <|-- IflrAndEflrBase
    LogicalRecordBase <|-- FileHeader
    LogicalRecordBase <|-- StorageUnitLabel
    
    IflrAndEflrBase <|-- IFLR
    IflrAndEflrBase <|-- EFLR
    
    IFLR <|-- FrameData
    IFLR <|-- NoFormatFrameData
    
    class LogicalRecordBase{
        +set_type
        +key
        +size
        +represent_as_bytes()
        +from_config()
    }
    
    class IflrAndEflrBase{
        +is_eflr
        +logical_record_type
        +segment_attributes
        +lr_type_struct
        +make_body_bytes()
        +make_header_bytes()
        +split()
        +make_lr_type_struct()
    }
    
    class EFLR{
        +dtime_formats
        +object_name
        +set_name
        +origin_reference
        +copy_number
        +obname
        -_rp66_rules
        -_attributes
        -_instance_dict
        +get_attribute()
        +set_attributes()
        +add_dependent_objects_from_config()
        +all_from_config()
        +get_or_make_from_config()
        +get_instance()
        -_create_attribute()
    }
    
    class FileHeader{
        +sequence_number
        +identifier
        +origin_reference
        +copy_number
        +object_name
    }
    
    class StorageUnitLabel{
        +storage_unit_structure
        +dlis_version
        +max_record_length
        +sequence_number
        +set_identifier
    }
```



```mermaid
---
title: IFLR objects and their relation to EFLR objects
---
classDiagram
    FrameData o-- "1" FrameItem
    NoFormatFrameData o-- "1" NoFormat
    
    class FrameData{
        +FrameItem frame
        +int frame_number
        +int origin_reference
        -slots numpy.ndarray
    }
    
    class NoFormatFrameData{
        +NoFormatItem no_format_object
        +Any data
    }
    
```