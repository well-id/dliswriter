.. _DLISFile:

DLISFile object
~~~~~~~~~~~~~~~
The ``DLISFile`` class, as shown in the :doc:`user guide <../../userguide/minimalexample>`,
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
This is the case both for *standalone* objects, such as :ref:`Message` or :ref:`Comment`, and the
potentially interlinked objects, such as :ref:`Zone` or :ref:`Parameter`.
(Note: adding a standalone :ref:`Channel` object is possible, but is known to cause issues in some readers,
e.g. *DeepView*.)
For this reason, in the ``dlis-writer`` implementation, adding objects in the `h5py` manner is only possible
from the top level - a ``DLISFile``:

.. code-block:: python

    dlis_file = DLISFile()
    logical_file = dlis_file.add_logical_file()  # a DLIS file is basically comprised of independent fully self-contained logical files
    a_channel = logical_file.add_channel(...)
    an_axis = logical_file.add_axis(...)


In order to mark relations between objects, a 'lower-level' object should be created first and then
passed as argument when creating a 'higher-level' object:

.. code-block:: python

    a_frame = logical_file.add_frame(..., channels=(a_channel, ...))   # frame can have multiple channels
    a_computation = logical_file.add_computation(..., axis=an_axis)    # computation can only have 1 axis


This makes it trivial to reuse already defined 'lower-level' objects as many times as needed:

.. code-block:: python

    # (multiple axes possible for both Parameter and Channel)
    a_param = logical_file.add_parameter(..., axis=(an_axis, ...))
    another_channel = logical_file.add_channel(..., axis=(an_axis, ...))


As shown in the :doc:`user guide <../../userguide/minimalexample>`, once all required objects are defined,
the ``write()`` method of ``DLISFile`` can be called to generate DLIS bytes and store them in a file.

Same-session incremental writing
--------------------------------

Use ``start_incremental(filename, initial_data, output_chunk_size=2**20)`` when
new batches arrive in the same process. This API supports exactly **one Logical
File and one Frame**, with no NoFormat data. It returns an
``IncrementalDLISWriter``; each ``append(batch)`` adds only FDATA, continuing the
frame numbering. The Storage Unit Label and metadata are written once.
``start_incremental`` writes ``initial_data`` immediately; the first ``append``
must supply the next batch, not repeat the initial data.

.. code-block:: python

    import numpy as np
    from dliswriter import DLISFile

    df = DLISFile()
    lf = df.add_logical_file()
    lf.add_origin("ORIGIN", origin_reference=1)
    signal = lf.add_channel("SIGNAL", units="V")
    lf.add_frame("FRAME", channels=[signal])

    initial = {"SIGNAL": np.arange(100, dtype=np.float32)}
    with df.start_incremental("new-output.dlis", initial) as stream:
        stream.append({"SIGNAL": np.arange(100, 200, dtype=np.float32)})
        stream.append({"SIGNAL": np.arange(200, 300, dtype=np.float32)})

``close()`` writes no extra records and is idempotent. Appending after closure
raises ``RuntimeError``. An existing output path raises ``FileExistsError``;
this is not an API for reopening or resuming a file. The destination is anchored
to an absolute path once at session start, before the existence check. Changing
the working directory later does not redirect appends. Existing symlinks,
including dangling symlinks, are rejected; this check provides no protection
against concurrent writers or external changes to the destination.

Fixed schema and batch safety
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The session detaches metadata from the caller's definition. Only missing channel
dtype, representation code, dimension and element limit are inferred from the
initial batch. Explicit structure must agree with that batch. Acquisition index
bounds, spacing and direction are **not** inferred from a partial batch: specify
them before starting when known, or leave them unknown for the whole session.
Later changes to the original definition do not change the session.
If ``index_type`` is specified, the first channel must have scalar samples
(a one-dimensional source array). With no ``index_type``, indexing is implicitly
by frame number and the first channel may have vector samples.

Batches may be dictionaries of NumPy arrays, one-dimensional structured NumPy
arrays, or HDF5 file paths (``.h5`` / ``.hdf5``). Every selected ``dataset_name``
must be present in each batch; data stored earlier on the Logical File is not
merged. Source key order may differ and extra datasets are ignored. Output uses
the Frame's channel order. Selected arrays must have equal positive row counts
and fixed scalar/vector sample shapes (one- or two-dimensional arrays).
HDF5 input handles are closed even when validation fails.

Supported numeric types are int8/16/32, uint8/16/32 and float32/64. Endianness is
normalized. Casts to the frozen effective dtype, including explicit
``cast_dtype``, must satisfy ``np.can_cast(source, target, casting="safe")``;
unsafe narrowing and object, string or complex arrays are rejected. This
API-specific policy does not change conventional ``write()`` behavior.

Each entire batch is normalized and materialized before emission, so memory use
scales with the batch, not the acquisition. Choose bounded batches;
``output_chunk_size`` must be an integer at least as large as the Storage Unit
Label's maximum record length. Prepared bytes use a private binary spool with
a fixed **1 MiB** in-memory threshold; larger representations spill to a temporary
file. Commit reads at most ``min(output_chunk_size, 1 MiB)`` bytes at a time.
The spool rolls over after a write, so its transient storage can exceed the
threshold by one visible record (or the initial 80-byte label). This bounds the
additional serialized representation, not input arrays, normalized batches,
materialized FDATA objects or individual serializer allocations.

Validation errors leave the output bytes and frame counter unchanged, allowing a
corrected batch to be retried. Any emission exception permanently fails the
session: future appends raise ``RuntimeError`` and partial bytes are not rolled
back. The counter advances only after successful emission. There are no
transactionality, crash/tail recovery, fsync, locking, concurrent-writer atomicity
or concurrent-reader guarantees. Keep the session in its original process and
do not modify its output file externally.

Before creating the destination, the session serializes the Storage Unit Label,
metadata and every initial FDATA record **once**, retaining their exact prepared
bytes through the writer's serialization, segmentation and visible-record
wrapping path. Appends prepare only new FDATA in the same way before modifying
the file. Commit copies the prepared stream without calling any serializers
again, even if serialization inferred defaults or changed object state. For example,
a too-short FDATA body or a maximum record length that cannot support segmenting
is rejected before output changes, even if construction of the definition was
valid. This is preflight validation, not rollback or an all-or-nothing I/O guarantee.
The session owns and closes the temporary spool on success and on preparation or
commit exceptions. A preparation failure permits retry without output changes.
If spool cleanup raises after commit started, the session is conservatively
failed and its counter is unchanged, even if all prepared bytes were copied.
