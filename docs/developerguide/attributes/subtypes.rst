Attribute subtypes
~~~~~~~~~~~~~~~~~~
Several ``Attribute`` subclasses have been defined to answer the reusable characteristics of the
attributes needed for various EFLR objects. The overview can be seen in the diagram below.

.. mermaid:: ../class-diagrams/attributes.mmd


``EFLRAttribute`` has been defined to deal with attributes which should keep reference to other
``EFLRItem`` s - for example, `Channel`_ s of `Frame`_, `Zone`_ s of `Splice`_,
`Calibration Coefficient`_ s and `Calibration Measurement`_ s of `Calibration`_.
The value of an ``EFLRAttribute`` is an instance of (usually specific subtype of) ``EFLRItem``.
The representation code can be either ``OBNAME`` or ``OBJREF``. The unit should not be defined (is meaningless).
Its subclass, ``EFLROrTextAttribute``, is similar, but in addition accepts plain text as value
(represented as ``ASCII``). This subclass is meant for the ``long_name`` attribute of `Channel`_,
`Process`_, and `Computation`_; the value of this attribute can be either text
or a ``LongNameItem`` object (`Long Name`_).

``DTimeAttribute`` is meant for keeping time reference, either in the form of a ``datetime.datetime`` object
or a number, indicating time since a specific event. The representation code is adapted
to the value: ``DTIME`` for ``datetime`` objects, otherwise any numeric code (e.g. ``FDOUBl``, ``USHORT``, etc.)
The unit should be defined if the value is a number and should express the unit of time
('s' for seconds, 'min' for minutes, etc.).

``NumericAttribute`` keeps numerical data - in the form of int(s) or float(s). It is possible
to restrict the type of accepted values to ints only or floats only at initialisation of the attribute.

``DimensionAttribute`` is a subclass of ``NumericAttribute``. It limits the above to ints only and is always
multivalued (always a list of integers). It is mainly used in [Channel](#channel) objects where it describes
the shape of the data (only the width, i.e. the number of columns).

``StatusAttribute`` encodes the status of `Tool`_ and `Equipment`_ objects.
Its value can only be 0 or 1.