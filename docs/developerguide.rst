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
