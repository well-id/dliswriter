.. _EFLRSet and EFLRItem:

EFLRSet and EFLRItem
~~~~~~~~~~~~~~~~~~~~
The implementation of the ELFRs is split over two separate classes: ``EFLRSet`` and ``EFLRItem``.
For the different schemes (as mentioned above), subclasses of both ``EFLRSet`` and ``EFLRItem`` are defined,
e.g. ``ChannelSet`` and ``ChannelItem``, ``FrameSet`` and ``FrameItem``, etc.

``EFLRItem`` is e.g. a single Channel, Frame, or Axis.
It has its own name (the first positional argument when initialising the object)
and a number of attributes (``Attribute`` instances; `DLIS Attributes`_), pre-defined by the standard.
For example, for a Channel, these attributes include: units, dimension, representation code,
minimum and maximum value, and others.

``EFLRSet`` can be viewed as a collection of ``EFLRItem`` instances.
Because a specific subclass of ``EFLRSet`` (e.g. ``ChannelSet``)
can only contain instances of a specific subclass of ``EFLRItem`` (e.g. ``ChannelItem``),
all ``EFLRItem`` s added to an ``EFLRSet`` will have exactly the same set of attribute types.
Therefore, an ``EFLRSet`` can be viewed as a table of ``EFLRItem`` s, with attribute names as table header
and individual ``EFLRItem`` with their attribute values as rows in that table.

As shown in the `LR types diagram`_ above, it is ``EFLRSet``, not ``EFLRItem``
that inherits from ``LogicalRecord`` base class. While this might be non-intuitive,
it is consistent with the standard; an Explicitly Formatted Logical Record in the standard is a table
as described above, with additional metadata.

Theoretically, multiple ``EFLRSet`` instances of the same type (e.g. multiple ``ChannelSet`` instances)
can be defined in a DLIS file. The key requirement is that their names - ``set_name`` - are different.
There cannot be two ``ChannelItem`` s (or two instances other ``EFLRItem`` subclass) with the same ``set_name``.
However, usually only a single instance of each ``EFLRSet`` is defined, and the default ``set_name`` is ``None``.

In the current implementation, there is usually no need to explicitly define ``EFLRSet`` (subclass) instances
or to interact with these. User is supposed to interact with the relevant ``EFLRItem`` subclass instead,
e.g. ``ChannelItem``, created through ``add_channel`` method of ``DLISFile`` instance.
