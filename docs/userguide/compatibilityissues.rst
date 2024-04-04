.. _Viewer issues:

Viewer compatibility issues
===========================

The DLIS format is defined by
`the RP66 v1 standard <https://energistics.org/sites/default/files/RP66/V1/Toc/main.html>`_.
This writer package strives to follow the standard as closely as sensible
while providing an easy-to-use interface.
However, it has been noticed that different DLIS viewers impose additional restrictions on the file format,
which may cause issues when opening files produced by this writer - even though the files conform to the standard.
Some of the known issues - and, if applicable, solutions - are described below.


PetroMar's DeepView
^^^^^^^^^^^^^^^^^^^
*   DeepView crashes if there is a :ref:`Channel` defined (added to the file e.g. by ``DLISFile.add_channel``)
    that is not added to any :ref:`Frame`. The standard doesn't seem to mention anything about it; it only says that
    no Channel object can be referenced by multiple Frames. The writer issues a log warning if a
    'freelancer' Channel is detected.
*   Some signed integer formats are not interpreted correctly, leading to erroneous overflow. Because these data are
    handled correctly by other viewers, no specific handling has been implemented in the writer.


Schlumberger's Log Data Composer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*   Names of all objects - Frames, Channels, etc. - must be uppercase. There is no mention about this in the standard.
    Other tested viewers accept lowercase names without any issue, so this is not handled in the writer in any way.
*   Requirements for the ``file_set_number`` of :ref:`Origin` are unclear. This value, if not specified by the user
    when the Origin is defined, is set to a randomly generated integer, in accordance with the standard.
    This, however, often makes Log Data Composer complain. If the generated DLIS file is meant for this software,
    it is recommended to explicitly set ``file_set_number`` to 1 when defining the Origin
    (e.g. by using the relevant keyword argument in the call to ``DLISFile.add_origin``).
*   Even though according to the standard, :ref:`Frame` spacing is meaningless if no index :ref:`Channel` is defined
    (see :ref:`Frame` for more details), Log Data Composer still requires a spacing defined.
    Therefore, in case of no index Channel, Frame spacing is internally set to 1 - if not specified by the user.
*   If an index Channel is defined, it must be made sure that the spacing of that Channel is uniform.
    (A warning in the logs is issued if this is not the case.)
    In case of non-uniform spacing, it is recommended to switch to implicit row-number indexing by removing
    ``index_type`` specification from the Frame; this is **not** done automatically.


Other things to look at
^^^^^^^^^^^^^^^^^^^^^^^
In case the generated DLIS file cannot be open in the target viewer software, there are a few more possible hints
to look at.

*   Some viewers require specific names for some objects, especially :ref:`Channel` s. For example, the index Channel
    - which might be required to represent depth - might have to be called "MD" (for "Measured Depth").
*   It is also recommended to not use spaces or special characters in the object names.
*   Specifying additional metadata for Channels - e.g. their minimum and maximum values - might help.
*   One should keep in mind that when ``index_type`` of :ref:`Frame` is specified, the first Channel of the Frame
    automatically becomes the index Channel. The data of this Channel should be 1D, monotonic, and, ideally,
    evenly spaced. Non-compliance with these requirements might cause the viewer to refuse to open the file or crash,
    even at a later stage (e.g. when scrolling through the data).
*   Some viewers might crash due to the sheer amount of data to view.
*   The :ref:`Path` object is known to cause issues in several viewers, including ``dlisio``.
    The cause of that is not well understood.


Loosened restrictions
^^^^^^^^^^^^^^^^^^^^^
In some cases, the standard defines a set of allowed values for a parameter - e.g. allowed unit symbols - but
the viewers are fine with using any value, as long as it has the same data type. In these cases, this writer also
allows the non-standard values, but issues a warning in the logs. This treatment has been applied to:

* units:
    * ``units`` :ref:`Attribute <Attribute>` of :ref:`Channel` s
        (``my_channel.units``, where ``units`` is an Attribute instance)
    * ``units`` part of Attributes of :ref:`EFLRs <EFLRs>` in general
        (e.g. ``my_frame.spacing.units``, where ``spacing`` is an Attribute instance)
* ``index_type`` of :ref:`Frame`
* ``type`` and ``location`` of :ref:`Equipment`


In other cases, the writer only allows the values specified by the standard. This is the case for:

* ``phase`` of :ref:`Calibration Measurement`
* ``status`` of :ref:`Process`
* ``domain`` of :ref:`Zone`
* ``properties`` of :ref:`Channel`, :ref:`Computation`, and :ref:`Process`
