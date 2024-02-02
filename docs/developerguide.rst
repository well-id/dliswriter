Developer guide
===============

This section describes the ``dlis-writer`` implementation in more detail.
The different types of logical records are explained.
Further, the principles of converting the Python objects to DLIS-compliant bytes are described.

Logical Records and Visible Records
-----------------------------------
:doc:`As mentioned before <aboutdlisformat>`, at an abstract level, DLIS file consists of multiple *logical records*
(LRs). They can be viewed as abstract units, containing a specific type of data and/or metadata.

On the other hand, in physical sense, a DLIS file is divided into *visible records* (VRs). They are byte structures
of pre-defined format, consisting of a 4-byte header (which includes a visible record start mark and record length)
and a body (which can be filled with any bytes carrying data and/or metadata, coming from the
logical records).

Visible records have a limited length, which is often lower than that of logical records.
In this case, the contents of a logical record can be split among several visible records' bodies.
The *logical record segments* (parts of the split logical record) contain additional
header information indicating e.g. whether the given segment is the first and/or the last one
of the original logical record.
(In case a logical record fits entirely into a single visible record, its body is also wrapped
in a logical record segment structure, with indication that the given segment is both
the first and the last part of the original logical record.)

The maximum length of a VR is defined in the file's *Storage Unit Label*.
According to the standard, the minimum length is not explicitly defined, but because the
minimum length of a LR segment is 16 bytes (including 4 LR segment header bytes),
the resulting minimum length of a VR is 20 bytes.

Logical Record types
--------------------
There are two main types of logical records: *Explicitly Formatted Logical Records* (EFLRs)
and *Indirectly Formatted Logical Records* (IFLRs).

The Storage Unit Label, the first record in the file,
could also be viewed as a logical record. However, due to functional discrepancies,
in the library, it does not inherit from the base ``LogicalRecord`` class; on the other hand,
it is implemented such that it can mock one and can be used alongside with actual ``LogicalRecord`` objects.

An overview of the types of logical records is shown below. _`LR types diagram`

.. mermaid:: class-diagrams/logical-record-types.mmd


Storage Unit Label
------------------
Storage Unit Label (SUL) takes up the first 80 bytes of each DLIS file.
Its format is different from that of other logical record types.

The attribute ``max_record_length`` of SUL determines the maximum length allowed for visible
records of the file (see `Logical Records and Visible Records`_),
expressed in bytes. This number is limited to 16384 and the default is 8192.

IFLR objects
------------
*IFLR*, or *Indirectly Formatted Logical Record* objects, are meant for keeping numerical or binary data.
There are two categories of IFLR:  `Frame Data`_ for strictly formatted numerical data
and `No-Format Frame Data`_ for arbitrary data bytes.

Frame Data
~~~~~~~~~~
Each Frame Data object represents a single row of formatted numerical data.
The order of values in a Frame Data must follow the order of Channels in the [Frame](#frame) it references.

For example, assume a Frame has 2 channels: 1D depth channel (``dimension=[1]``)
and 2D image channel with 128 columns (``dimension=[128]``).
The generated FrameData objects should contain 129 values:
1 from the depth channel followed by 128 from a row of the image channel.
The values are merged into a single, flat array.

In the library, Frame Data objects are generated automatically from Frame object information and data referenced
by the relevant channels; see [MultiFrameData](./src/dlis_writer/file/multi_frame_data.py) for the procedure.

No-Format Frame Data
~~~~~~~~~~~~~~~~~~~~
No-Format Frame Data is a wrapper for unformatted data - arbitrary bytes the user wishes to save in the file.
It must reference a [No-Format](#no-format) object. The data - as bytes or str - should be added in the
``data`` attribute. An arbitrary number of NOFORMAT FrameData can be created.

IFLR objects and their relations to EFLR objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The relations of Frame Data and No-Format Frame-Data to their 'parent' EFLR objects is summarised below.
For explanation on the differences between ``FrameSet`` and ``FrameItem`` etc., please see `EFLRSet and EFLRItem`_.

.. mermaid:: class-diagrams/iflrs-vs-eflrs.mmd


EFLR objects
------------
*Explicitly Formatted Logical Records* are meant for representing metadata according to pre-defined schemes.
More than 20 such schemes are defined (see `Implemented EFLR objects`_).
Each one lists a specific set of attributes.
Some of the EFLRs are required for a DLIS file: *File Header*, *Origin*,
*Frame*, and *Channels*. Others are optional ways of specifying more metadata.

EFLRSet and EFLRItem
~~~~~~~~~~~~~~~~~~~~
The implementation of the ELFRs is split over two separate classes: ``EFLRSet`` and ``EFLRItem``.
For the different schemes (as mentioned above), subclasses of both ``EFLRSet`` and ``EFLRItem`` are defined,
e.g. ``ChannelSet`` and ``ChannelItem``, ``FrameSet`` and ``FrameItem``, etc.

``EFLRItem`` is e.g. a single Channel, Frame, or Axis.
It has its own name (the first positional argument when initialising the object)
and a number of attributes (``Attribute`` instances; `DLIS Attributes`_), pre-defined by the standard.
For example, for a Channel, these attributes include: units, dimension, representation code,
minimum and maximum value, and others.

``EFLRSet`` can be viewed as a collection of ``EFLRItem`` instances.
Because a specific subclass of ``EFLRSet`` (e.g. ``ChannelSet``)
can only contain instances of a specific subclass of ``EFLRItem`` (e.g. ``ChannelItem``),
all ``EFLRItem`` s added to an ``EFLRSet`` will have exactly the same set of attribute types.
Therefore, an ``EFLRSet`` can be viewed as a table of ``EFLRItem`` s, with attribute names as table header
and individual ``EFLRItem`` with their attribute values as rows in that table.

As shown in the `LR types diagram`_ above, it is ``EFLRSet``, not ``EFLRItem``
that inherits from ``LogicalRecord`` base class. While this might be non-intuitive,
it is consistent with the standard; an Explicitly Formatted Logical Record in the standard is a table
as described above, with additional metadata.

Theoretically, multiple ``EFLRSet`` instances of the same type (e.g. multiple ``ChannelSet`` instances)
can be defined in a DLIS file. The key requirement is that their names - ``set_name`` - are different.
There cannot be two ``ChannelItem`` s (or two instances other ``EFLRItem`` subclass) with the same ``set_name``.
However, usually only a single instance of each ``EFLRSet`` is defined, and the default ``set_name`` is ``None``.

In the current implementation, there is usually no need to explicitly define ``EFLRSet`` (subclass) instances
or to interact with these. User is supposed to interact with the relevant ``EFLRItem`` subclass instead,
e.g. ``ChannelItem``, created through ``add_channel`` method of ``DLISFile`` instance.


Implemented EFLR objects
~~~~~~~~~~~~~~~~~~~~~~~~
The types of EFLRs implemented in this library are described below.
Note: the standard defines several more types of EFLRs.

File Header
^^^^^^^^^^^
File Header must immediately follow a `Storage Unit Label`_ of the file.
Its length must be exactly 124 bytes.
The ``identifier`` attribute of the File Header represents the name of the DLIS file.
It should be a string of max 65 characters.

Origin
^^^^^^
Every DLIS file must contain at least one Origin. Usually, it immediately follows the `File Header`_.
The Origin keeps key information related to the scanned well, the scan procedure, producer, etc.
The ``creation_time`` attribute of Origin, if not explicitly specified, is set to the current
date and time (when the object is initialised).

The ``file_set_number`` attribute of an Origin (assigned by user or randomly generated) is used as an Origin reference
in other DLIS objects. By default, the ``file_set_number`` of the first defined Origin is assigned to all other objects.
To indicate that an object originally comes from a different file, the user should create an additional Origin
with the relevant information and pass its ``file_set_number`` when creating the objects belonging to that Origin.

From RP66:
    ORIGIN Objects uniquely identify Logical Files and describe the basic circumstances under which Logical Files
    are created. ORIGIN Objects also provide a means for distinguishing different instances of a given entity.
    Each Logical File must contain at least one ORIGIN Set, which may contain one or more ORIGIN Objects.
    The first Object in the first ORIGIN Set is the Defining Origin for the Logical File in which it is contained,
    and the corresponding Logical File is called the Origin’s Parent File.
    It is intended that no two Logical Files will ever have Defining Origins with all Attribute Values identical.

Channel
^^^^^^^
Channel is meant for wrapping and describing data sets.
A single channel refers to a single column of data (a single curve, e.g. depth, time, rpm)
or a 2D data set (an image, e.g. amplitude, radius).

From RP66:
    Channel Objects (...) identify Channels and specify their properties and their representation in Frames.
    The actual Channel sample values are recorded in Indirectly Formatted Logical Records, when present.

In the standard, Channel does not directly contain the data it refers to, but rather described
the data's properties, such as the unit and representation code.

The dimension and element limit express the horizontal shape of the data, i.e. the number of columns.
It is always a list of integers. List of any length would be accepted, but because this implementation
only handles 1D and 2D data, this is always a single-element list: ``[1]`` for 1D datasets
and ``[n]`` for 2D datasets, where ``n`` is the number of columns in the image (usually 128).
In this implementation, dimension and element limit should have the same value.
Setting one at initialisation of Channel automatically sets up the other in the same way.

A `Frame`_ always refers to a list of channels. The order is important; the first channel
is used as the index. When a row of data is stored (wrapped in a `Frame Data`_ object),
the order of channels as passed to the Frame is preserved.

Channels can also be referred to by `Splice`_, `Path`_, `Calibration`_,
`Calibration Measurement`_, `Process`_, and `Tool`_.

On the receiving end, Channel can reference an `Axis`_ and/or a `Long Name`_.

Frame
^^^^^
Frame is a collection of `Channel`_ s. It can be interpreted as a table of numerical data.
Channels can be viewed as variable-width, vertical slices of a Frame.
Information contained in the Frame (and Channels) is used to generate `Frame Data`_ objects,
which are horizontal slices of Frame - this time, strictly one row per slice.

Frame has an ``index_type`` ``Attribute``, which defines the kind of data used as the common index
for all (other) channels in the Frame. The values explicitly allowed by standard are:
'ANGULAR-DRIFT', 'BOREHOLE-DEPTH', 'NON-STANDARD', 'RADIAL-DRIFT', and 'VERTICAL-DEPTH'.
However, because most readers accept other expressions for index type, this library also allows it,
only issuing a warning in the logs.

Additional metadata defining a Frame can include its direction ('INCREASING' or 'DECREASING'),
spacing (a float value + unit), as well as ``index_max`` and ``index_min``.
These values are needed for some DLIS readers to interpret the data correctly.
Therefore, if not explicitly specified by the user, these values are inferred from the data
(in particular, from the first channel passed to the frame), if the frame setup allows.

Frame can be referenced by `Path`_.

From RP66:
    A Frame constitutes the Indirectly Formatted Data of a Type FDATA Indirectly Formatted Logical Record (IFLR).
    The Data Descriptor Reference of the FDATA Logical Record refers to a Frame Object (...)
    and defines the Frame Type of the Frame.
    Frames of a given Frame Type occur in sequences within a single Logical File.
    A Frame is segmented into a Frame Number, followed by a fixed number of Slots that contain Channel samples,
    one sample per Slot. The Frame Number is an integer (Representation Code UVARI) specifying the numerical order
    of the Frame in the Frame Type, counting sequentially from one. All Frames of a given Frame Type record the same
    Channels in the same order. The IFLRs containing Frames of a given Type need not be contiguous.

    A Frame Type may or may not have an Index Channel. If there is an Index Channel, then it must appear first
    in the Frame and it must be scalar. When an Index Channel is present, then all Channels in the Frame are assumed
    to be "sampled at" the Index value. For example, if the Index is depth, then Channels are sampled at the given
    depth; if time, then they are sampled at the given time, etc. (...)

    The truth of the assumption just stated is relative to the measuring and recording system used and does not
    imply absolute accuracy. For example, depth may be measured by a device that monitors cable movement
    at the surface, which may differ from actual tool movement in the borehole. Corrections that are applied
    to Channels to improve the accuracy of measurements or alignments to indices are left to the higher-level
    semantics of applications.

    When there is no Index Channel, then Frames are implicitly indexed by Frame Number.

Axis
^^^^
Axis defines coordinates (expressed either as floats or strings, e.g ``"40 23' 42.8676'' N"`` is a valid coordinate)
and spacing. Axis can be referenced by `Calibration Measurement`_,
`Channel`_, `Parameter`_, and `Computation`_.

From RP66:
    An Axis Logical Record is an Explicitly Formatted Logical Record that contains information
    describing the coordinate axes of arrays.

Calibration Coefficient
^^^^^^^^^^^^^^^^^^^^^^^
Calibration Coefficient describes a set of coefficients together with reference values and tolerances.
It can be referenced by `Calibration`_.

From RP66:
    Calibration-Coefficient Objects record coefficients, their references, and tolerances
    used in the calibration of Channels.

Calibration Measurement
^^^^^^^^^^^^^^^^^^^^^^^
Calibration Measurement describes measurement performed for the purpose of calibration.
It can reference a `Channel`_ object and can be referenced by `Calibration`.

From RP66:
    Calibration-Measurement Objects record measurements, references, and tolerances used to compute
    calibration coefficients.

Calibration
^^^^^^^^^^^
Calibration object describes a calibration with performed measurements (`Calibration Measurement`_)
and associated coefficients (`Calibration Coefficient`_). It can also reference
`Channel`_ s and `Parameter`_ s.
The ``method`` of a calibration is a string description of the applied method.

From RP66:
    Calibration Objects identify the collection of measurements and coefficients that participate
    in the calibration of a Channel.

Computation
^^^^^^^^^^^
A Computation can reference an `Axis`_, `Zone`_ s, and a `LongName`.
Additionally, through ``source`` ``Attribute``, it can reference another object being the direct source
of this computation, e.g. a `Tool`_.
Computation can be referenced by a `Process`_.

The number of values specified for the ``values`` ``Attribute`` must match the number of `Zone`_ s
added to the Computation (through ``zones`` ``Attribute``).

From RP66:
    Computation Objects (...) contain results of computations that are more appropriately expressed as Static
    Information rather than as Channels. Computation Objects are similar to Parameter Objects, except that
    Computation Objects may be associated with Property Indicators, and Computation Objects may be the output
    of PROCESS Objects (...).

Equipment
^^^^^^^^^
Equipment describes a single part of a `Tool`_, specifying its trademark name, serial number, etc.
It also contains float data on parameters such as: height, length, diameter, volume, weight,
hole size, pressure, temperature, radial and angular drift.
Each of these values can (and should) have a unit assigned.

From RP66:
    Equipment Objects (...) specify the presence and characteristics of surface and downhole equipment
    used in the acquisition of data. The purpose of this Object is to record information about individual pieces
    of equipment of any sort that is used during a job. The Tool Object (...) provides a way to collect equipment
    together in ensembles that are more readily recognizable to the Consumer.

Group
^^^^^
A Group can refer to multiple other EFLR objects of a given type.
It can also keep references to other groups, creating a hierarchical structure.

Long Name
^^^^^^^^^
Long Name specifies various string attributes of an object to describe it in detail.
It can be referenced by `Channel`_, `Computation`_, or `Parameter`_.

From RP66:
    Long-Name Objects represent structured names of other Objects.
    A Long–Name Object is referenced by (an Attribute of) the Object of which it is the structured name.
    There are standardized Name Part Types corresponding to the Labels of the Attributes of the Long-Name Object.
    For each Name Part Type there is a dictionary-controlled Lexicon of Name Part Values.
    A Name Part Value is a word or phrase. The Long Name is built by selecting those Name Part Types
    that are applicable to an Object and then selecting for each Name Part Type one or more Name Part Values
    from the corresponding Lexicons.

Message
^^^^^^^
A Message is a string value with associated metadata - such as time
(``datetime`` or float - number of minutes/seconds/etc. since a specific event),
borehole/radial/angular drift, and vertical depth.

Comment
^^^^^^^
A Comment is simpler than a `Message`_ object; it contains only the comment text.

No-Format
^^^^^^^^^
No-Format is a metadata container for unformatted data `No-Format Frame Data`_.
It allows users to write arbitrary bytes of data.
Just like `Frame`_ can be thought of as a collection of `Frame Data`_ objects,
No-Format is a collection of `No-Format Frame Data`_ objects.

No-Format specifies information such as consumer name and description of the associated data.

From RP66:
    Unformatted Data Logical Records are Indirectly Formatted Logical Records of Type NOFORM that contain
    "packets" of unformatted (in the DLIS sense) binary data. The Data Descriptor reference of the NOFORM
    Logical Record refers to a NO-FORMAT Object (...). The purpose of Unformatted Data Logical Records is
    to transport arbitrary data that is of value to the Consumer, the format of which is known by the Consumer,
    but which has no DLIS Semantic meaning.

    NO-FORMAT Objects identify packet sequences of unformatted binary data. The Indirectly Formatted Data field
    of each NOFORM IFLR that references a given No-Format Object contains a segment of the source stream
    of unformatted data. This source stream is recovered by concatenating these segments in the same order
    in which they occur in the NOFORM IFLRs. Each segment of the source stream is considered under the DLIS
    to be a sequence of bytes, and no conversion is applied to the bytes as they are placed into the IFLRs
    nor as they are removed from the IFLRs.

Parameter
^^^^^^^^^
A Parameter is a collection of values, which can be either numbers or strings.
It can reference `Zone`_, `Axis`_, and `Long Name`_.
It can be referenced by `Calibration`_, `Process`_, and `Tool`_.

From RP66:
    Parameter Objects (...) specify Parameters (constant or zoned) used in the acquisition and processing of data.
    Parameters may be scalar-valued or array-valued. When they are array-valued, the semantic meaning
    of the array dimensions is defined by the application.

Path
^^^^
Path describes several numerical values - such as angular/radial drift and measurement offsets -
of the well. It can also reference a `Frame`_, `Well Reference Point`_,
and `Channel`_ s.

From RP66:
    Path Objects specify which Channels in the Data Frames of a given Frame Type are combined to define part or all
    of a Data Path, and what variations in alignment exist.
    The Index of a Frame Type automatically and explicitly serves as a Locus component of any Data Path represented
    in the Frame Type whenever Frame Attribute INDEX-TYPE has one of the values angular-drift, borehole-depth,
    radial-drift, time, or vertical-depth.

Process
^^^^^^^
A Process combines multiple other objects: Channel`_ s, `Computation`_ s,
and `Parameter`_ s.

From RP66:
    [Each Process] describes a specific process or computation applied to input Objects to get output Objects.

The ``status`` ``Attribute`` of Process can be one of: 'COMPLETE', 'ABORTED', 'IN-PROGRESS'.

Splice
^^^^^^
A Splice relates several input and output `Channel`_ s and `Zone` s.

From RP66:
    Splice Objects describe the process of concatenating two or more instances of a Channel
    (e.g., from different runs) to get a resultant spliced Channel.

Tool
^^^^
A Tool is a collection of `Equipment`_ objects (stored in the ``parts`` ``Attribute``).
It can also reference `Channel`_ s and `Parameter`_ s,
and can be referenced by `Computation`_.

From RP66:
    Tool Objects (...) specify ensembles of equipment that work together to provide specific measurements
    or services. Such combinations are more recognizable to the Consumer than are their individual pieces.
    A typical tool consists of a sonde and a cartridge and possibly some appendages such as centralizers
    and spacers. It is also possible to identify certain pieces or combinations of surface measuring equipment
    as tools.

Well Reference Point
^^^^^^^^^^^^^^^^^^^^
Well Reference Point can be used to specify up to 3 coordinates of a point. The coordinates
should be expressed as floats.
Well Reference Point can be referenced by `Path`_.

From RP66:
    Each well has a Well Reference Point (WRP) that defines the origin of the well’s spatial coordinate system.
    The Well Reference Point is a fixed point in space defined for each Origin. This point is defined relative
    to some permanent structure, such as ground level or mean sea level. It need not coincide with the permanent
    structure, but its vertical distance from the permanent structure must be stated. (...)
    Spatial coordinates of a well are depth, Radial Drift, and Angular Drift. Depth is defined in terms of
    Borehole Depth or Vertical Depth.

Zone
^^^^
A zone specifies a single interval in depth or time.
The ``domain`` of a Zone can be one of: 'BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH'.
The expression of ``minimum`` and ``maximum`` of a Zone depends on the domain.
For 'TIME', they could be ``datetime`` objects or floats (indicating the time since a specific event;
in this case, specifying a time unit is also advisable).
For the other domains, they should be floats, ideally with depth units (e.g. 'm').

Zone can be referenced by `Splice`_, `Process`_, or `Parameter`_.

From RP66:
    Zone Objects specify single intervals in depth or time. Zone Objects are useful for associating other Objects
    or values with specific regions of a well or with specific time intervals.


Relations between EFLR objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Many of the EFLR objects are interrelated - e.g. a Frame refers to multiple Channels,
each of which can have an Axis; a Calibration uses Calibration Coefficients and Calibration Measurements;
a Tool has Equipments as parts. The relations are summarised in the diagram below.

*Note*: in the diagrams below, the description of ``Attribute`` s of the objects has been simplified.
Only the type of the ``.value`` part of each ``Attribute`` is shown - e.g. in ``CalibrationItem``,
``calibrated_channels`` is shown as a list of ``ChannelItem`` instances, where in fact it is
an ``EFLRAttribute`` whose ``.value`` takes the form of a list of ``ChannelItem`` objects.

.. mermaid:: class-diagrams/eflr-relations.mmd


Other EFLR objects can be thought of as _standalone_ - they do not refer to other EFLR objects
and are not explicitly referred to by any (although - as in case of NoFormat - a relation to IFLR objects can exist).

.. mermaid:: class-diagrams/standalone-eflrs.mmd


A special case is a `Group`_ object, which can refer to any other EFLRs or other groups,.

.. mermaid:: class-diagrams/group-object.mmd


DLIS Attributes
---------------
The characteristics of EFLR (``EFLRItem``) objects of the DLIS are defined using instances of ``Attribute`` class.
An ``Attribute`` holds the value of a given parameter together with the associated unit (if any)
and a representation code which guides how the contained information is transformed to bytes.
Allowed units (not a strict set) and representation codes are defined in the code
(although explicit setting of representation codes is no longer possible).

The Attribute class
~~~~~~~~~~~~~~~~~~~~~
The main characteristics of ``Attribute`` are described below.

* ``label``: The name of the ``Attribute``. Comes from the standard and should not be changed.
* ``value``: The value(s) specified for this ``Attribute``. In general, any type is allowed, but in most cases it is
  (a list of): str / int / float / ``EFLRItem`` / ``datetime``.
* ``multivalued``: a Boolean indicating whether this ``Attribute`` instance accepts a list of values (if True)
  or a single value (if False). Specified at initialisation of the ``Attribute`` (which usually takes place
  at initialisation of the relevant EFLR object).
* ``multidimensional``: a Boolean indicating whether the value of this ``Attribute`` can have multiple dimensions
  (be represented as a nested list). If True, ``multivalued`` must also be True.
* ``count``: Number of values specified for the ``Attribute`` instance. If the ``Attribute`` is not ``multivalued``,
  ``count`` is always 1. Otherwise, it is the number of values added to the ``Attribute`` (or ``None`` if no value
  is given).
* ``units``: A string representing the units of the ``value`` of the ``Attribute`` - if relevant.
  The standard pre-defines a list of allowed units, but many DLIS readers accept any string value.
  For this reason, only a log warning is issued if the user specifies a unit other than those given by the standard.
* ``representation_code``: indication of type of the value(s) of the ``Attribute`` and guidance on how they should be
  converted to bytes to be included in the file. Representation codes are either defined when the Attribute
  is initialised or are inferred from the provided value(s). They are not settable by the user.
* ``parent_eflr``: The ``EFLRItem`` instance this attribute belongs to. Mainly used for string representation
  of the ``Attribute`` (e.g. ``Attribute 'description' of ToolItem 'TOOL-1'``, where ``TOOL-1`` is the parent EFLR).
* ``converter``: A callable which is used to convert the value passed by the user (or each of the individual items
  if the ``Attribute`` is multivalued) to fit the standard-imposed requirements for the given ``Attribute``. It can also
  include type checks etc. (for example, checking that the objects passed to ``calibrated_channels``
  of ``CalibrationItem``) are all instances of ``ChannelItem``.

*Settable* parts of ``Attribute`` instance include: ``value``, ``units``, and ``converter``.
Some subtypes of ``Attribute`` further restrict what can be set.


Attribute subtypes
~~~~~~~~~~~~~~~~~~
Several ``Attribute`` subclasses have been defined to answer the reusable characteristics of the
attributes needed for various EFLR objects. The overview can be seen in the diagram below.

.. mermaid:: class-diagrams/attributes.mmd


``EFLRAttribute`` has been defined to deal with attributes which should keep reference to other
``EFLRItem`` s - for example, `Channel`_ s of `Frame`_, `Zone`_ s of `Splice`_,
`Calibration Coefficient`_ s and `Calibration Measurement`_ s of `Calibration`_.
The value of an ``EFLRAttribute`` is an instance of (usually specific subtype of) ``EFLRItem``.
The representation code can be either ``OBNAME`` or ``OBJREF``. The unit should not be defined (is meaningless).
Its subclass, ``EFLROrTextAttribute``, is similar, but in addition accepts plain text as value
(represented as ``ASCII``). This subclass is meant for the ``long_name`` attribute of `Channel`_,
`Process`_, and `Computation`_; the value of this attribute can be either text
or a ``LongNameItem`` object (`Long Name`_).

``DTimeAttribute`` is meant for keeping time reference, either in the form of a ``datetime.datetime`` object
or a number, indicating time since a specific event. The representation code is adapted
to the value: ``DTIME`` for ``datetime`` objects, otherwise any numeric code (e.g. ``FDOUBl``, ``USHORT``, etc.)
The unit should be defined if the value is a number and should express the unit of time
('s' for seconds, 'min' for minutes, etc.).

``NumericAttribute`` keeps numerical data - in the form of int(s) or float(s). It is possible
to restrict the type of accepted values to ints only or floats only at initialisation of the attribute.

``DimensionAttribute`` is a subclass of ``NumericAttribute``. It limits the above to ints only and is always
multivalued (always a list of integers). It is mainly used in [Channel](#channel) objects where it describes
the shape of the data (only the width, i.e. the number of columns).

``StatusAttribute`` encodes the status of `Tool`_ and `Equipment`_ objects.
Its value can only be 0 or 1.


Writing the binary file
-----------------------
The objects described above are Python representation of the information to be included in a DLIS file.
Subsections below explain how these objects are converted to bytes, which then become a part of the created file.

DLISFile object
~~~~~~~~~~~~~~~
The ``DLISFile`` class, as shown in the :doc:`user guide <userguide>`,
is the main point of the user's interaction with the library.
It facilitates defining a (future) file with all kinds of EFLR and IFLR objects and the relations between them.

The interface was initially inspired by that of ``h5py``, in particular the HDF5-writer part of it:
the *child* objects (e.g. HDF5 *datasets*) can be created and simultaneously linked to the *parent* objects
(e.g. HDF5 *groups*) by calling a relevant method of the parent instance like so:

.. code-block:: python

    new_h5_dataset = some_h5_group.add_dataset(...)

However, while the HDF5 structure is strictly hierarchical, the same cannot be said about DLIS.
For example, the same Zone can be referenced by multiple Splices, Parameters, and Computations.
It is also possible to add any object without it referencing or being referenced by other objects.
This is the case both for _standalone_ objects, such as Message or Comment, and the
potentially interlinked objects, such as Zone or Parameter.
(Note: adding a standalone Channel object is possible, but is known to cause issues in some readers, e.g. *DeepView*.)
For this reason, in the ``dlis-writer`` implementation, adding objects in the `h5py` manner is only possible
from the top level - a ``DLISFile``:

.. code-block:: python

    dlis_file = DLISFile()
    a_channel = dlis_file.add_channel(...)
    an_axis = dlis_file.add_axis(...)


In order to mark relations between objects, a 'lower-level' object should be created first and then
passed as argument when creating a 'higher-level' object:

.. code-block:: python

    a_frame = dlis_file.add_frame(..., channels=(a_channel, ...))   # frame can have multiple channels
    a_computation = dlis_file.add_computation(..., axis=an_axis)    # computation can only have 1 axis


This makes it trivial to reuse already defined 'lower-level' objects as many times as needed:

.. code-block:: python

    # (multiple axes possible for both Parameter and Channel)
    a_param = dlis_file.add_parameter(..., axis=(an_axis, ...))
    another_channel = dlis_file.add_channel(..., axis=(an_axis, ...))


As shown in the :doc:`user guide <userguide>`, once all required objects are defined,
the ``write()`` method of ``DLISFile`` can be called to generate DLIS bytes and store them in a file.


Ways of passing data
~~~~~~~~~~~~~~~~~~~~
Data associated with the file's Channels can be passed when adding a Channel to the ``DLISFile`` instance.
Data added in this way is stored in an internal dictionary, mapped by the Channels' names.

However, it is also possible to pass the data later, when calling the ``write()`` method
of the ``DLISFile``. The passed data can be of one of the following forms:

* A dictionary of ``numpy.ndarray`` s (1D or 2D, depending on the Channel configuration).
  The keys of the dictionary must match the ``dataset_name`` s of the Channels added to the file.
  (If not explicitly specified, the ``dataset_name`` of a Channel is the same as its name.)
* A structured ``numpy.ndarray``, whose *dtype names* match the ``dataset_name`` s of the Channels.
* A path to an HDF5 file, containing the relevant datasets. In this case, the Channels' ``dataset_name`` s
  must define the full internal paths to the datasets starting from the root of the file - e.g.
  ``/contents_root/general_group/specific_group/the_dataset``.

Note: even if multiple Frames are defined, the data object passed to the ``write()`` call should contain
all datasets to be included in the file. The correct arrangement of the datasets is done internally
at a later stage. The data is also allowed to contain datasets not to be used in the file;
these will simply be ignored. However, the writing cannot be done if data for any of the Channels are missing.

The data are then internally wrapped in a ``SourceDataWrapper``,
in particular one of its subclasses - designed for handling ``dict``, ``numpy.ndarray``, or HDF5 data.
The main objectives of these objects are:

* ensuring the correct structure (order of channels etc.) of the data when ``FrameData`` instances are created
* loading the source data in chunks rather than the entire data at a time to address memory limitations.

Note that because creating the required structure is the responsibility of the library,
not the user, it is assumed that the provided data will not match the needed structure.
In order to create the (chunks of) structured numpy array needed for Frame Data, the source data must be copied.
The ``SourceDataWrapper`` objects copy only as much data as are needed to define a single data chunk for writing.
When that chunk is exhausted, the 'used' data are discarded and a new chunk is loaded.

The size of the input data chunk is defined in number of rows of the data table.
It can be controlled by setting ``input_chunk_size`` in the ``write()`` call of the ``DLISFile``.
The optimal value varies depending on the structure of the data (number & widths of the individual datasets)
as well as the hardware configuration.


DLISWriter and auxiliary objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``DLISWriter`` is the object where the bytes creation and writing to file happens.
Given the iterable of logical records, provided by the ``DLISFile``,
a ``DLISWriter`` iterates over the logical records and for each one:

#. Assigns an _origin_reference_ to all objects in the file.
   The origin reference is the ``file_set_number`` of the Origin object defined in the file.
#. Calls for creation of bytes describing that logical record
   (see `Converting objects and attributes to bytes`_)
#. If the bytes sequence is too long to fit into a single visible record,
   it splits the bytes into several segments (see [the explanation](#logical-records-and-visible-records))
#. Wraps the segments (or full bytes sequence) in visible records and writes the resulting bytes to a file.

The writing of bytes is aided by objects of two auxiliary classes: ``ByteWriter`` and ``BufferedOutput``.
The main motivation between both is to facilitate gradual, _chunked_ writing of bytes to a file
rather than having to keep everything in memory and dumping it to the file at the very end.

``ByteWriter`` manages access to the created DLIS file. Its ``write_bytes()`` method,
which can be called repetitively, writes or appends the provided bytes to the file.
The object also keeps track of the total size (in bytes) of the file as it is being created.

The role of ``BufferedOutput`` is to gather bytes of the created visible records
and periodically call the ``write_bytes()`` of the ``ByteWriter`` to send the collected
bytes to the file and clear its internal cache, getting ready for receiving more bytes.
The size of the gathered bytes chunk is user-tunable through ``output_chunk_size`` argument to the
``write()`` method of the ``DLISFile``.
It can be adjusted to tackle the tradeoff between the amount of data stored in memory at any given point
and the number of I/O calls.


Converting objects and attributes to bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The way in which different objects are converted to DLIS-compliant bytes
depends on the category these objects fall into, according to the earlier specified
[division](#logical-record-types).

* `Storage Unit Label`_ has its own predefined bytes structure of fixed length.
  Its content varies minimally, taking into account the parameters specified at its creation,
  such as visible record length, storage set identifier, etc.
* The main part of `Frame Data`_ (IFLR) - the numerical data associated with the Channels - is stored
  in the object as a row od a structured ``numpy.ndarray``. Each entry of the array is converted to
  bytes using the ``numpy`` 's built-in ``tobytes()`` method (with additional ``byteswap()`` call before that
  to account for the big-endianness of DLIS). Additional bytes referring to the [Frame](#frame)
  and the index of the current Frame Data in the Frame are added on top.
* In `No-Format Frame Data`_, the *data* part can be already expressed as bytes,
  in which case it is used as-is. Otherwise, it is assumed to be of string type and is encoded as ASCII.
  A reference to the parent `No-Format`_ object is added on top.
* EFLR objects (`EFLRSet and EFLRItem`_) are treated per ``EFLRSet`` instance.

    * First, bytes describing the ``EFLRSet`` instance are made, including its ``set_type``
      and ``set_name`` (if present).
    * Next, *template* bytes are added. These specify the order and names of ``Attribute`` s
      characterising the ``EFLRItem`` instances belonging to the given ``EFLRSet``.
    * Finally, each of the ``EFLRItem`` 's bytes are added. Bytes of an ``EFLRItem`` instance consist of
      its name + *origin reference* + *copy number* description, followed by the values and other characteristics
      (units, repr. codes, etc.) of each of its ``Attribute`` s in the order specified in the
      ``EFLRSet`` 's *template*.

