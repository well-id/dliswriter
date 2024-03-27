Relations between EFLR objects
==============================
Many of the EFLR objects are interrelated - e.g. a Frame refers to multiple Channels,
each of which can have an Axis; a Calibration uses Calibration Coefficients and Calibration Measurements;
a Tool has Equipments as parts. The relations are summarised in the diagram below.

*Note*: in the diagrams below, the description of ``Attribute`` s of the objects has been simplified.
Only the type of the ``.value`` part of each ``Attribute`` is shown - e.g. in ``CalibrationItem``,
``calibrated_channels`` is shown as a list of ``ChannelItem`` instances, where in fact it is
an ``EFLRAttribute`` whose ``.value`` takes the form of a list of ``ChannelItem`` objects.

.. mermaid:: ../../class-diagrams/eflr-relations.mmd


Other EFLR objects can be thought of as _standalone_ - they do not refer to other EFLR objects
and are not explicitly referred to by any (although - as in case of NoFormat - a relation to IFLR objects can exist).

.. mermaid:: ../../class-diagrams/standalone-eflrs.mmd


A special case is a `Group`_ object, which can refer to any other EFLRs or other groups,.

.. mermaid:: ../../class-diagrams/group-object.mmd

