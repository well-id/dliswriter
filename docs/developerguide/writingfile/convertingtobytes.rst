.. _Converting to bytes:

Converting objects and attributes to bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The way in which different objects are converted to DLIS-compliant bytes
depends on the category these objects fall into, according to the earlier specified :ref:`division <LR types>`.

* :ref:`SUL` has its own predefined bytes structure of fixed length.
  Its content varies minimally, taking into account the parameters specified at its creation,
  such as visible record length, storage set identifier, etc.
* The main part of :ref:`Frame Data` (:ref:`IFLR <IFLRs>`) - the numerical data associated
  with the :ref:`Channel` s - is stored
  in the object as a row od a structured ``numpy.ndarray``. Each entry of the array is converted to
  bytes using the ``numpy`` 's built-in ``tobytes()`` method (with additional ``byteswap()`` call before that
  to account for the big-endianness of DLIS). Additional bytes referring to the :ref:`Frame`
  and the index of the current Frame Data in the Frame are added on top.
* In :ref:`No-Format Frame Data`, the data part can be already expressed as bytes,
  in which case it is used as-is. Otherwise, it is assumed to be of string type and is encoded as ASCII.
  A reference to the parent :ref:`No-Format` object is added on top.
* EFLR objects (:ref:`EFLRSet and EFLRItem`) are treated per ``EFLRSet`` instance.

    * First, bytes describing the ``EFLRSet`` instance are made, including its ``set_type``
      and ``set_name`` (if present).
    * Next, *template* bytes are added. These specify the order and names of ``Attribute`` s
      characterising the ``EFLRItem`` instances belonging to the given ``EFLRSet``.
    * Finally, each of the ``EFLRItem`` 's bytes are added. Bytes of an ``EFLRItem`` instance consist of
      its name + *origin reference* + *copy number* description, followed by the values and other characteristics
      (units, repr. codes, etc.) of each of its ``Attribute`` s in the order specified in the
      ``EFLRSet`` 's *template*.

