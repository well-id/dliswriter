DLIS Enums
==========

Values of certain attributes of the DLIS objects can only be chosen from pre-defined sets of values,
specified by `the standard <https://energistics.org/sites/default/files/RP66/V1/Toc/main.html>`_.
To facilitate the correct setup of these attributes, the ``dlis_writer`` package defines a number of enumerations,
which can be used as shown in :ref:`the examples <User guide more objects>` before (see e.g. how the Zones are set up).
The implemented enumerations are listed below. They are available from ``dlis_writer.enums``.

* ``Unit`` enum
   * for ``units`` :ref:`Attribute <Attribute>` of :ref:`Channel`\ s (``my_channel.units``, where ``units`` is an Attribute instance)
   * ``units`` part of Attributes of :ref:`EFLRs <EFLRs>` in general (e.g. ``my_frame.spacing.units``, where ``spacing`` is an Attribute instance)
* ``FrameIndexType`` enum for ``index_type`` Attribute of :ref:`Frame`
* ``EquipmentType`` enum for ``type`` Attribute of :ref:`Equipment`
* ``EquipmentLocation`` enum for ``location`` Attribute of :ref:`Equipment`
* ``CalibrationMeasurementPhase`` enum for ``phase`` Attribute of :ref:`Calibration Measurement`
* ``ProcessStatus`` enum for ``status`` Attribute of :ref:`Process`
* ``ZoneDomain`` enum for ``domain`` of :ref:`Zone`
* ``Property`` enum for ``properties`` Attribute of:
   * :ref:`Channel`
   * :ref:`Computation`
   * :ref:`Process`
