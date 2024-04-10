Relations between EFLR objects
==============================
Many of the :ref:`EFLR <EFLRs>` objects are interrelated - e.g. a :ref:`Frame` refers to multiple :ref:`Channel`\ s,
each of which can have an :ref:`Axis`;
a :ref:`Calibration` uses :ref:`Calibration Coefficient`\ s and :ref:`Calibration Measurement`\ s;
a :ref:`Tool` has :ref:`Equipment`\ s as parts. The relations are summarised in the diagram below.

*Note*: in the diagrams below, the description of :ref:`Attribute`\ s of the objects has been simplified.
Only the type of the ``.value`` part of each ``Attribute`` is shown - e.g. in ``CalibrationItem``,
``calibrated_channels`` is shown as a list of ``ChannelItem`` instances, where in fact it is
an ``EFLRAttribute`` whose ``.value`` takes the form of a list of ``ChannelItem`` objects.

.. mermaid:: ../../class-diagrams/eflr-relations.mmd


Other :ref:`EFLR <EFLRs>` objects can be thought of as standalone - they do not refer to other EFLR objects
and are not explicitly referred to by any
(although - as in case of :ref:`No-Format` - a relation to :ref:`IFLR <IFLRs>` objects can exist).

.. mermaid:: ../../class-diagrams/standalone-eflrs.mmd


A special case is a :ref:`Group` object, which can refer to any other :ref:`EFLRs <EFLRs>` or other groups,.

.. mermaid:: ../../class-diagrams/group-object.mmd

