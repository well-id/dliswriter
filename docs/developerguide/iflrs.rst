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
