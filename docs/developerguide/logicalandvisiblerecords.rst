Logical Records and Visible Records
-----------------------------------
:doc:`As mentioned before <../aboutdlisformat>`, at an abstract level, DLIS file consists of multiple *logical records*
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
