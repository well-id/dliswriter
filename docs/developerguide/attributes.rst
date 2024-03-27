DLIS Attributes
---------------
The characteristics of EFLR (``EFLRItem``) objects of the DLIS are defined using instances of ``Attribute`` class.
An ``Attribute`` holds the value of a given parameter together with the associated unit (if any)
and a representation code which guides how the contained information is transformed to bytes.
Allowed units (not a strict set) and representation codes are defined in the code
(although explicit setting of representation codes is no longer possible).

The Attribute class
~~~~~~~~~~~~~~~~~~~~~
The main characteristics of ``Attribute`` are described below.

* ``label``: The name of the ``Attribute``. Comes from the standard and should not be changed.
* ``value``: The value(s) specified for this ``Attribute``. In general, any type is allowed, but in most cases it is
  (a list of): str / int / float / ``EFLRItem`` / ``datetime``.
* ``multivalued``: a Boolean indicating whether this ``Attribute`` instance accepts a list of values (if True)
  or a single value (if False). Specified at initialisation of the ``Attribute`` (which usually takes place
  at initialisation of the relevant EFLR object).
* ``multidimensional``: a Boolean indicating whether the value of this ``Attribute`` can have multiple dimensions
  (be represented as a nested list). If True, ``multivalued`` must also be True.
* ``count``: Number of values specified for the ``Attribute`` instance. If the ``Attribute`` is not ``multivalued``,
  ``count`` is always 1. Otherwise, it is the number of values added to the ``Attribute`` (or ``None`` if no value
  is given).
* ``units``: A string representing the units of the ``value`` of the ``Attribute`` - if relevant.
  The standard pre-defines a list of allowed units, but many DLIS readers accept any string value.
  For this reason, only a log warning is issued if the user specifies a unit other than those given by the standard.
* ``representation_code``: indication of type of the value(s) of the ``Attribute`` and guidance on how they should be
  converted to bytes to be included in the file. Representation codes are either defined when the Attribute
  is initialised or are inferred from the provided value(s). They are not settable by the user.
* ``parent_eflr``: The ``EFLRItem`` instance this attribute belongs to. Mainly used for string representation
  of the ``Attribute`` (e.g. ``Attribute 'description' of ToolItem 'TOOL-1'``, where ``TOOL-1`` is the parent EFLR).
* ``converter``: A callable which is used to convert the value passed by the user (or each of the individual items
  if the ``Attribute`` is multivalued) to fit the standard-imposed requirements for the given ``Attribute``. It can also
  include type checks etc. (for example, checking that the objects passed to ``calibrated_channels``
  of ``CalibrationItem``) are all instances of ``ChannelItem``.

*Settable* parts of ``Attribute`` instance include: ``value``, ``units``, and ``converter``.
Some subtypes of ``Attribute`` further restrict what can be set.


Attribute subtypes
~~~~~~~~~~~~~~~~~~
Several ``Attribute`` subclasses have been defined to answer the reusable characteristics of the
attributes needed for various EFLR objects. The overview can be seen in the diagram below.

.. mermaid:: class-diagrams/attributes.mmd


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
