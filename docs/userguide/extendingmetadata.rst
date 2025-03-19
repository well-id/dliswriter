Extending basic metadata
========================
As mentioned above, initialising :ref:`DLISFile` automatically constructs :ref:`Storage Unit Label <SUL>`
and each initialised LogicalFile constructs :ref:`File Header`.
However, the definition of each of these can be further tuned.
The same applies to :ref:`Origin`, which is the container for key meta-data concerning the well, company, operation set-up etc.

.. code-block:: python

    from dlis_writer.file import DLISFile

    # define DLISFile passing more information for creating Storage Unit Label and File Header
    df = DLISFile(
      set_identifier="MY-SET",
      sul_sequence_number=5,
      max_record_length=4096,
    )

    first_logical_file = df.add_logical_file(
      fh_id=in_fheaderid_truncated,
      fh_sequence_number=int(in_fheader.sequencenr),
      fh_identifier=str(int(in_fheader.name)),
    )

    # add Origin with more details
    # see more available keyword arguments in DLISFile.add_origin()
    origin = first_logical_file.add_origin(
      'MY-ORIGIN',
      file_set_name='MY-FILE-SET-NAME',
      file_set_number=11,
      file_number=22,
      well_id="55",
      well_name='MY-WELL'
    )


The attributes can also be changed later by accessing the relevant objects' attributes.
Note: because most attributes are instances of :ref:`Attribute <Attribute>` class,
you will need to use ``.value`` (or ``.unit``) of the attribute you may want to change.

.. code-block:: python

    origin.company.value = "COMPANY X"

