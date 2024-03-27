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


As per the logical records relations graph (see the :doc:`Developer guide <../developerguide/developerguide>`),
Zone objects can be used to define e.g. Splice objects (which also refer to Channels):

.. code-block:: python

    splice1 = df.add_splice('SPLICE1', input_channels=(ch1, ch2), output_channel=ch3, zones=(zone1, zone2))


For more objects, see example file at ``examples/create_synth_dlis.py``
and the description of all implemented objects in the :doc:`Developer guide <../developerguide/developerguide>`.

Definition of all additional objects should precede the call to ``.write()`` of ``DLISFile``,
otherwise no strict order is observed.
