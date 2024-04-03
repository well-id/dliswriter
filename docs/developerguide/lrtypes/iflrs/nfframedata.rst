.. _No-Format Frame Data:

No-Format Frame Data
~~~~~~~~~~~~~~~~~~~~
No-Format Frame Data is a wrapper for unformatted data - arbitrary bytes the user wishes to save in the file.
It must reference a :ref:`No-Format` object. The data - as bytes or str - should be added in the
``data`` attribute. An arbitrary number of No-Format Frame Data objects can be created.
