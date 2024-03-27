DLIS Attributes
---------------
The characteristics of EFLR (``EFLRItem``) objects of the DLIS are defined using instances of ``Attribute`` class.
An ``Attribute`` holds the value of a given parameter together with the associated unit (if any)
and a representation code which guides how the contained information is transformed to bytes.
Allowed units (not a strict set) and representation codes are defined in the code
(although explicit setting of representation codes is no longer possible).

.. toctree::
   :maxdepth: 2

   attribute
   subtypes
