# `dlis-writer` example scripts

Scripts in this folder illustrate the basic usage of the library.

- [create_synth_dlis.py](./examples/create_synth_dlis.py) shows how to add every kind 
of DLIS object to the file - including Parameters, Equipment, Comments, No-Formats, etc.
It is also shown how multiple frames (in this case, a depth-based and a time-based frame) can be defined.

- [create_dlis_equivalent_frames.py](./examples/create_dlis_from_data.py) shows how to make a DLIS file containing multiple frames of the same 
structure (the same set of channel names etc.).

- [create_dlis_from_data.py](./examples/create_dlis_from_data.py) can be used to make a DLIS file
from a hdf5, csv, las, and xlx/xlsx data source.

- [create_synth_dlis_variable_data.py](./examples/create_synth_dlis_variable_data.py) allows creating DLIS files
with any number of 2D datasets with a user-defined shape, filled with randomised data. 


