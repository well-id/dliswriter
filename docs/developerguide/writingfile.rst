Writing the binary file
-----------------------
The objects described above are Python representation of the information to be included in a DLIS file.
Subsections below explain how these objects are converted to bytes, which then become a part of the created file.

DLISFile object
~~~~~~~~~~~~~~~
The ``DLISFile`` class, as shown in the :doc:`user guide <../userguide/userguide>`,
is the main point of the user's interaction with the library.
It facilitates defining a (future) file with all kinds of EFLR and IFLR objects and the relations between them.

The interface was initially inspired by that of ``h5py``, in particular the HDF5-writer part of it:
the *child* objects (e.g. HDF5 *datasets*) can be created and simultaneously linked to the *parent* objects
(e.g. HDF5 *groups*) by calling a relevant method of the parent instance like so:

.. code-block:: python

    new_h5_dataset = some_h5_group.add_dataset(...)

However, while the HDF5 structure is strictly hierarchical, the same cannot be said about DLIS.
For example, the same Zone can be referenced by multiple Splices, Parameters, and Computations.
It is also possible to add any object without it referencing or being referenced by other objects.
This is the case both for _standalone_ objects, such as Message or Comment, and the
potentially interlinked objects, such as Zone or Parameter.
(Note: adding a standalone Channel object is possible, but is known to cause issues in some readers, e.g. *DeepView*.)
For this reason, in the ``dlis-writer`` implementation, adding objects in the `h5py` manner is only possible
from the top level - a ``DLISFile``:

.. code-block:: python

    dlis_file = DLISFile()
    a_channel = dlis_file.add_channel(...)
    an_axis = dlis_file.add_axis(...)


In order to mark relations between objects, a 'lower-level' object should be created first and then
passed as argument when creating a 'higher-level' object:

.. code-block:: python

    a_frame = dlis_file.add_frame(..., channels=(a_channel, ...))   # frame can have multiple channels
    a_computation = dlis_file.add_computation(..., axis=an_axis)    # computation can only have 1 axis


This makes it trivial to reuse already defined 'lower-level' objects as many times as needed:

.. code-block:: python

    # (multiple axes possible for both Parameter and Channel)
    a_param = dlis_file.add_parameter(..., axis=(an_axis, ...))
    another_channel = dlis_file.add_channel(..., axis=(an_axis, ...))


As shown in the :doc:`user guide <../userguide/userguide>`, once all required objects are defined,
the ``write()`` method of ``DLISFile`` can be called to generate DLIS bytes and store them in a file.


Ways of passing data
~~~~~~~~~~~~~~~~~~~~
Data associated with the file's Channels can be passed when adding a Channel to the ``DLISFile`` instance.
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

Note: even if multiple Frames are defined, the data object passed to the ``write()`` call should contain
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
In order to create the (chunks of) structured numpy array needed for Frame Data, the source data must be copied.
The ``SourceDataWrapper`` objects copy only as much data as are needed to define a single data chunk for writing.
When that chunk is exhausted, the 'used' data are discarded and a new chunk is loaded.

The size of the input data chunk is defined in number of rows of the data table.
It can be controlled by setting ``input_chunk_size`` in the ``write()`` call of the ``DLISFile``.
The optimal value varies depending on the structure of the data (number & widths of the individual datasets)
as well as the hardware configuration.


DLISWriter and auxiliary objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``DLISWriter`` is the object where the bytes creation and writing to file happens.
Given the iterable of logical records, provided by the ``DLISFile``,
a ``DLISWriter`` iterates over the logical records and for each one:

#. Assigns an _origin_reference_ to all objects in the file.
   The origin reference is the ``file_set_number`` of the Origin object defined in the file.
#. Calls for creation of bytes describing that logical record
   (see `Converting objects and attributes to bytes`_)
#. If the bytes sequence is too long to fit into a single visible record,
   it splits the bytes into several segments (see [the explanation](#logical-records-and-visible-records))
#. Wraps the segments (or full bytes sequence) in visible records and writes the resulting bytes to a file.

The writing of bytes is aided by objects of two auxiliary classes: ``ByteWriter`` and ``BufferedOutput``.
The main motivation between both is to facilitate gradual, _chunked_ writing of bytes to a file
rather than having to keep everything in memory and dumping it to the file at the very end.

``ByteWriter`` manages access to the created DLIS file. Its ``write_bytes()`` method,
which can be called repetitively, writes or appends the provided bytes to the file.
The object also keeps track of the total size (in bytes) of the file as it is being created.

The role of ``BufferedOutput`` is to gather bytes of the created visible records
and periodically call the ``write_bytes()`` of the ``ByteWriter`` to send the collected
bytes to the file and clear its internal cache, getting ready for receiving more bytes.
The size of the gathered bytes chunk is user-tunable through ``output_chunk_size`` argument to the
``write()`` method of the ``DLISFile``.
It can be adjusted to tackle the tradeoff between the amount of data stored in memory at any given point
and the number of I/O calls.


Converting objects and attributes to bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The way in which different objects are converted to DLIS-compliant bytes
depends on the category these objects fall into, according to the earlier specified
[division](#logical-record-types).

* `Storage Unit Label`_ has its own predefined bytes structure of fixed length.
  Its content varies minimally, taking into account the parameters specified at its creation,
  such as visible record length, storage set identifier, etc.
* The main part of `Frame Data`_ (IFLR) - the numerical data associated with the Channels - is stored
  in the object as a row od a structured ``numpy.ndarray``. Each entry of the array is converted to
  bytes using the ``numpy`` 's built-in ``tobytes()`` method (with additional ``byteswap()`` call before that
  to account for the big-endianness of DLIS). Additional bytes referring to the [Frame](#frame)
  and the index of the current Frame Data in the Frame are added on top.
* In `No-Format Frame Data`_, the *data* part can be already expressed as bytes,
  in which case it is used as-is. Otherwise, it is assumed to be of string type and is encoded as ASCII.
  A reference to the parent `No-Format`_ object is added on top.
* EFLR objects (`EFLRSet and EFLRItem`_) are treated per ``EFLRSet`` instance.

    * First, bytes describing the ``EFLRSet`` instance are made, including its ``set_type``
      and ``set_name`` (if present).
    * Next, *template* bytes are added. These specify the order and names of ``Attribute`` s
      characterising the ``EFLRItem`` instances belonging to the given ``EFLRSet``.
    * Finally, each of the ``EFLRItem`` 's bytes are added. Bytes of an ``EFLRItem`` instance consist of
      its name + *origin reference* + *copy number* description, followed by the values and other characteristics
      (units, repr. codes, etc.) of each of its ``Attribute`` s in the order specified in the
      ``EFLRSet`` 's *template*.

