User guide
==========
In the sections below you can learn how to define and write a DLIS file using the ``dlis-writer``.

Minimal example
---------------
Below you can see a very minimal DLIS file example with two 1D channels (one of which serves as the index)
and a single 2D channel.

.. code-block:: python

    import numpy as np  # for creating mock datasets
    from dlis_writer.file import DLISFile  # the main dlis-writer object you will interact with

    # create a DLISFile object
    # this also initialises Storage Unit Label and File Header with minimal default information
    df = DLISFile()

    # add Origin
    df.add_origin("MY-ORIGIN")

    # number of rows for creating the datasets
    # all datasets (channels) belonging to the same frame must have the same number of rows
    n_rows = 100

    # define channels with numerical data and additional information
    #  1) the first channel is also the index channel of the frame;
    #     must be 1D, ideally should be monotonic and equally spaced
    ch1 = df.add_channel('DEPTH', data=np.arange(n_rows) / 10, units='m')

    #  2) second channel; in this case 1D and unitless
    ch2 = df.add_channel("RPM", data=(np.arange(n_rows) % 10).astype(float))

    #  3) third channel - an image channel (2D data)
    ch3 = df.add_channel("AMPLITUDE", data=np.random.rand(n_rows, 5))

    # define frame, referencing the above defined channels
    main_frame = df.add_frame("MAIN-FRAME", channels=(ch1, ch2, ch3), index_type='BOREHOLE-DEPTH')

    # when all the required objects have been added, write the data and metadata to a physical DLIS file
    df.write('./new_dlis_file.DLIS')


Extending basic metadata
------------------------
As mentioned above, initialising ``DLISFile`` object automatically constructs Storage Unit Label and File Header.
However, the definition of each of these can be further tuned.
The same applies to Origin, which is the container for key meta-data concerning the well, company, operation set-up etc.

.. code-block:: python

    from dlis_writer.file import DLISFile

    # define DLISFile passing more information for creating Storage Unit Label and File Header
    df = DLISFile(
      set_identifier="MY-SET",
      sul_sequence_number=5,
      max_record_length=4096,
      fh_id="MY-FILE-HEADER",
      fh_sequence_number=8
    )

    # add Origin with more details
    # see more available keyword arguments in DLISFile.add_origin()
    origin = df.add_origin(
      'MY-ORIGIN',
      file_id='MY-FILE-ID',
      file_set_name='MY-FILE-SET-NAME',
      file_set_number=11,
      file_number=22,
      well_id=55,
      well_name='MY-WELL'
    )


The attributes can also be changed later by accessing the relevant objects's attributes.
Note: because most attributes are instances of ``Attribute`` class,
you will need to use ``.value`` (or ``.unit``) of the attribute you may want to change.

.. code-block:: python

    origin.company.value = "COMPANY X"


Adding more objects
-------------------
Adding other logical records to the file is done in the same way as adding channels and frames.
For example, to add a zone (in depth or in time):

.. code-block:: python

    zone1 = df.add_zone('DEPTH-ZONE', domain='BOREHOLE-DEPTH', minimum=2, maximum=4.5)
    zone2 = df.add_zone('TIME-ZONE', domain='TIME', minimum=10, maximum=30)


To specify units for numerical values, you can use ``.units`` of the relevant attribute, e.g.

.. code-block:: python

    zone1.minimum.units = 'in'  # inches
    zone2.maximum.units = 's'   # seconds


It is also possible to pass the units together with the value, using a ``dict``:

.. code-block:: python

    zone3 = df.add_zone('VDEPTH-ZONE', domain='VERTICAL-DEPTH',
                        minimum={'value': 10, 'units': 'm'}, maximum={'value': 30, 'units': 'm'})


As per the logical records relations graph (see the :doc:`Developer guide <developerguide>`),
Zone objects can be used to define e.g. Splice objects (which also refer to Channels):

.. code-block:: python

    splice1 = df.add_splice('SPLICE1', input_channels=(ch1, ch2), output_channel=ch3, zones=(zone1, zone2))


For more objects, see example file at ``examples/create_synth_dlis.py``
and the description of all implemented objects in the :doc:`Developer guide <developerguide>`.

Definition of all additional objects should precede the call to ``.write()`` of ``DLISFile``,
otherwise no strict order is observed.
