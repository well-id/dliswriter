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
todo


DLIS Attributes
---------------
todo
