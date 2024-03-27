Storage Unit Label
------------------
Storage Unit Label (SUL) takes up the first 80 bytes of each DLIS file.
Its format is different from that of other logical record types.

The attribute ``max_record_length`` of SUL determines the maximum length allowed for visible
records of the file (see `Logical Records and Visible Records`_),
expressed in bytes. This number is limited to 16384 and the default is 8192.
