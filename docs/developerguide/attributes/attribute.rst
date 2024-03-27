.. _Attribute:

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
