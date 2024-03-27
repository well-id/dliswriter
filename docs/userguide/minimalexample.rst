Minimal example
===============
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
