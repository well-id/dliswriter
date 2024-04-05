About the DLIS format
=====================

`DLIS (Digital Log Information Standard) <https://energistics.org/sites/default/files/RP66/V1/Toc/main.html>`_.
is a binary data format dedicated to storing well log data.
It was developed in the 1980's, when data were stored on magnetic tapes.
Despite numerous advances in the field of information technology, DLIS is still prevalent in the oil and gas industry.

A DLIS file is composed of :ref:`logical records <LR types>` - topical units containing pieces of data and/or metadata.
There are multiple subtypes of logical records which are predefined for specific types of (meta)data.
The most important ones are mentioned below, with more extensive descriptions
in the :doc:`Developer guide <./developerguide/index>`.

Every DLIS file starts with a logical record called :ref:`Storage Unit Label (SUL) <SUL>`,
followed by a :ref:`File Header`. Both of these mainly contain format-specific metadata.

A file must also have at least one :ref:`Origin`, which holds the key information
about the scanned well, scan procedure, producer, etc.

Numerical data are kept in a :ref:`Frame`, composed of several :ref:`Channels <Channel>`.
A channel can be interpreted as a single curve ('column' of data) or a single image (2D data).

Additional metadata can be specified using dedicated logical records subtypes,
such as :ref:`Parameter`, :ref:`Zone`, :ref:`Calibration`, :ref:`Equipment`, etc.
See :doc:`the list <./developerguide/lrtypes/eflrs/implemented>` for more details.
Additionally, for possible relations between the different objects,
see the relevant :doc:`class diagrams <./developerguide/lrtypes/eflrs/relations>`.

**Note**: this writer package has been developed in accordance with the
`RP66 v1 standard <https://energistics.org/sites/default/files/RP66/V1/Toc/main.html>`_.
Automatic testing of the writer functionalities and standard compliance has been done with the help of
`dlisio Python package <https://dlisio.readthedocs.io/en/latest/>`_.
The files produced by the writer have also been tested in PetroMar's DeepView and Schlumberger's Log Data Composer
software; however, some :ref:`viewer-specific issues <Viewer issues>` have been observed, mainly caused by additional assumptions
on the file format made in those viewers.
