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

An overview of the types of logical records is shown below.

..mermaid:: class-diagrams/logical-record-types.mmd


Storage Unit Label
------------------
Storage Unit Label (SUL) takes up the first 80 bytes of each DLIS file.
Its format is different from that of other logical record types.

The attribute ``max_record_length`` of SUL determines the maximum length allowed for visible
records of the file (see :ref:`Logical Records and Visible Records`_),
expressed in bytes. This number is limited to 16384 and the default is 8192.

IFLR objects
------------
*IFLR*, or *Indirectly Formatted Logical Record* objects, are meant for keeping numerical or binary data.
There are two categories of IFLR:  :ref:`Frame Data`_ for strictly formatted numerical data
and :ref:`No-Format Frame Data`_ for arbitrary data bytes.

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
For explanation on the differences between ``FrameSet`` and ``FrameItem`` etc., please see [here](#eflrset-and-eflritem).

..mermaid:: class-diagrams/iflrs-vs-eflrs.mmd
