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
