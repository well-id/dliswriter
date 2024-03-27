Logical Record types
--------------------
There are two main types of logical records: *Explicitly Formatted Logical Records* (EFLRs)
and *Indirectly Formatted Logical Records* (IFLRs).

The Storage Unit Label, the first record in the file,
could also be viewed as a logical record. However, due to functional discrepancies,
in the library, it does not inherit from the base ``LogicalRecord`` class; on the other hand,
it is implemented such that it can mock one and can be used alongside with actual ``LogicalRecord`` objects.

An overview of the types of logical records is shown below. _`LR types diagram`

.. mermaid:: class-diagrams/logical-record-types.mmd
