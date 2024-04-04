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
TODO


Schlumberger's Log Data Composer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TODO


Other things to look at
^^^^^^^^^^^^^^^^^^^^^^^
TODO


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
