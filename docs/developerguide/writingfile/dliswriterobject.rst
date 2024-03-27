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

