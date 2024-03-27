About the DLIS format
=====================

DLIS (Digital Log Information Standard) is a binary data format dedicated to storing well log data.
It was developed in the 1980's, when data were stored on magnetic tapes.
Despite numerous advances in the field of information technology, DLIS is still prevalent in the oil and gas industry.

A DLIS file is composed of *logical records* - topical units containing pieces of data and/or metadata.
There are multiple subtypes of logical records which are predefined for specific types of (meta)data.
The most important ones are mentioned below, with more extensive descriptions
in the :doc:`Developer guide <./developerguide/index>`.

Every DLIS file starts with a logical record called *Storage Unit Label (SUL)*,
followed by a *File Header*. Both of these mainly contain format-specific metadata.

A file must also have at least one *Origin*, which holds the key information
about the scanned well, scan procedure, producer, etc.

Numerical data are kept in a *Frame*, composed of several *Channels*.
A channel can be interpreted as a single curve ('column' of data) or a single image (2D data).

Additional metadata can be specified using dedicated logical records subtypes,
such as *Parameter*, *Zone*, *Calibration*, *Equipment*, etc.
See :doc:`the list <./developerguide/lrtypes/eflrs/implemented>` for more details.
Additionally, for possible relations between the different objects,
see the relevant :doc:`class diagrams <./developerguide/lrtypes/eflrs/relations>`.
