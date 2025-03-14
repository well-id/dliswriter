.. _Viewer issues:

Viewer compatibility issues
===========================

The DLIS format is defined by
`the RP66 v1 standard <https://energistics.org/sites/default/files/RP66/V1/Toc/main.html>`_.
This writer package strives to follow the standard as closely as sensible
while providing an easy-to-use interface.
However, it has been noticed that different DLIS viewers impose additional restrictions on the file format,
which may cause issues when opening files produced by this writer - even though the files conform to the standard.

.. _hc_mode:

High-compatibility mode
-----------------------
For the above-described reason, DLIS Writer has a *high-compatibility mode*.
In this mode, the writer raises errors in case a potential viewer issue is detected.

The mode can be activated by using a dedicated context manager:

.. code-block:: python

    from dlis_writer import high_compatibility_mode

    with high_compatibility_mode:
        # your code goes here

For example, when lowercase characters are used in channel names (see issues with :ref:`schlumberger`),
the following code:

.. code-block:: python

    with high_compatibility_mode:
        df = DLISFile()
        lf = df.add_logical_file()
        lf.add_origin("MY-ORIGIN")
        ch1 = lf.add_channel('Depth', data=np.arange(100) / 10, units=Renums.Unit.METER)


will raise a ``ValueError``:

.. code-block:: python

    ValueError: In high-compatibility mode, strings can contain only uppercase characters, digits, dashes, and underscores; got 'Depth'

Without the high-compatibility mode context, the writer will only issue a log warning with the same message.

Known issues
------------
Some of the known issues - and, if applicable, solutions - are described below.
*Standard handling* in the descriptions below refers to the default handling as described in the :ref:`hc_mode` section:
an error is raised or a log warning is issued depending on whether or not the high-compatibility mode context is used.


PetroMar's DeepView
^^^^^^^^^^^^^^^^^^^
*   DeepView crashes if there is a :ref:`Channel` defined (added to the file e.g. by ``DLISFile.add_channel``)
    that is not added to any :ref:`Frame`. The standard doesn't seem to mention anything about it; it only says that
    no Channel object can be referenced by multiple Frames. :ref:`Standard handling <hc_mode>` applies.
*   Signed integer formats are not interpreted correctly, leading to erroneous overflow (negative values are
    represented as large positive ones). :ref:`Standard handling <hc_mode>` applies.


.. _schlumberger:

Schlumberger's Log Data Composer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*   Names of all objects - Frames, Channels, etc. - must be uppercase. :ref:`Standard handling <hc_mode>` applies.
    To be on the safe side, spaces and special characters are also not accepted in the high-compatibility mode.
*   Requirements for the ``file_set_number`` of :ref:`Origin` are unclear. This value, if not specified by the user
    when the Origin is defined, is set to a randomly generated integer, in accordance with the standard.
    This, however, often makes Log Data Composer complain. In :ref:`hc_mode`, the ``file_set_number`` is automatically
    set to the index of the Origin in the current ``OriginSet`` (1 for the first Origin, 2 for the second, etc.)
*   Even though according to the standard, :ref:`Frame` spacing is meaningless if no index :ref:`Channel` is defined
    (see :ref:`Frame` for more details), Log Data Composer still requires a spacing defined.
    Therefore, in case of no index Channel, Frame spacing is internally set to 1 - if not specified by the user.
    This is done regardless of whether the high-compatibility mode is used or not.
*   If an index Channel is defined, it must be made sure that the spacing of that Channel is uniform.
    :ref:`Standard handling <hc_mode>` applies.
    In case of non-uniform spacing, it is recommended to switch to implicit row-number indexing by removing
    ``index_type`` specification from the Frame.


Other things to look at
^^^^^^^^^^^^^^^^^^^^^^^
In case the generated DLIS file cannot be open in the target viewer software, there are a few more possible hints
to look at.

*   Some viewers require specific names for some objects, especially :ref:`Channel`\ s. For example, the index Channel
    - which might be required to represent depth - might have to be called "MD" (for "Measured Depth").
*   Specifying additional metadata for Channels - e.g. their minimum and maximum values - might help.
*   One should keep in mind that when ``index_type`` of :ref:`Frame` is specified, the first Channel of the Frame
    automatically becomes the index Channel. The data of this Channel should be 1D, monotonic, and, ideally,
    evenly spaced. Non-compliance with these requirements might cause the viewer to refuse to open the file or crash,
    even at a later stage (e.g. when scrolling through the data).
*   Some viewers might crash due to the sheer amount of data to view.
*   The :ref:`Path` object is known to cause issues in several viewers, including ``dlisio``.
    The cause of that is not well understood.


Loosened restrictions
---------------------
In some cases, the standard defines a set of allowed values for a parameter - e.g. allowed unit symbols - but
the viewers are fine with using any value, as long as it has the same data type. In these cases, this writer also
allows the non-standard values, but issues a warning in the logs. This treatment has been applied to:

* ``units`` (both as Attribute of :ref:`Channel` and as part of other Attributes)
* ``index_type`` of :ref:`Frame`
* ``type`` and ``location`` of :ref:`Equipment`

Note: in :ref:`hc_mode`, only the pre-defined values for these parameters are accepted.
