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


