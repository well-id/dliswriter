Ways of passing data
~~~~~~~~~~~~~~~~~~~~
Data associated with the file's :ref:`Channel` s can be passed when adding a :ref:`Channel`
to the ``DLISFile`` instance.
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

Note: even if multiple :ref:`Frame` s are defined, the data object passed to the ``write()`` call should contain
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
In order to create the (chunks of) structured numpy array needed for :ref:`Frame Data`, the source data must be copied.
The ``SourceDataWrapper`` objects copy only as much data as are needed to define a single data chunk for writing.
When that chunk is exhausted, the 'used' data are discarded and a new chunk is loaded.

The size of the input data chunk is defined in number of rows of the data table.
It can be controlled by setting ``input_chunk_size`` in the ``write()`` call of the ``DLISFile``.
The optimal value varies depending on the structure of the data (number & widths of the individual datasets)
as well as the hardware configuration.


