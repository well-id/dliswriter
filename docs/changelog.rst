Changelog
=========

Version 1.0.1
-------------
* Project logo visibility fix for PyPI.

Version 1.0.0
-------------
**First public release!**

* Specified licence for the project: `MIT <https://choosealicense.com/licenses/mit/>`_.
* Added README badges for an appearance boost.
* Completed docs wherever they were missing.
* Designed the `logo <https://github.com/well-id/dliswriter/blob/master/logo.png>`_.
* Lowered minimum required Python version to 3.9.
* Limited the number of dependencies.


Version 0.0.10
--------------
**High-compatibility mode**

* Added *high-compatibility mode* in the form of a context manager. All potential issues are raised as errors.
* Described potential compatibility issues in different DLIS viewers.
* Implemented additional checks on the channels and data of channels in frames and frame index.
* Added :ref:`DLIS Enums` for more robust value checks where a set of allowed values is pre-defined.
* Re-factored and updated documentation.


Version 0.0.9
-------------
**Multiple Origins, processing input files, documentation**

* Added the possibility to have multiple Origin objects in the created file.
  The first added Origin is automatically used as the *defining Origin* of the file, but an alternative Origin reference
  can be set for each created DLIS object. See ``examples/create_synth_dlis.py``.
* Made ``file_set_number`` an optional argument for creating Origin;
  instead, it's generated randomly in accordance with the RP66 standard.
* Added scripts to write data from .xls/.xlsx, .csv, and .las files to a basic DLIS
  (in addition to the preexisting .h5/.hdf5 converter).
  See the ``dlis_writer/file_format_converter`` subpackage
  and the related example: ``examples/create_dlis_from_data.py``.
* Added quotes from RP66 to docstrings of ``add_<object>`` methods of ``DLISFile``.
* Implemented additional restrictions specified by the standard - e.g. dimensionality of values, number of zones vs
  number of values, number of axis coordinates vs dimension/value, etc.
* Added the possibility for LongName objects to be referenced by Channel, Computation, and Parameter.


Version 0.0.8
-------------
**API improvements & fixes**

* Removed representation code setters from ``Attribute``.
* More value type and representation code (repr code inferred from value) checks.
* Setting up ``Attribute`` values and units together using ``dict`` or a new ``AttrSetup`` class.
* ``DLISFile``: ``add_origin`` method; origin instance or setup keywords no longer accepted in ``DLISFile`` init.
* Support for defining multiple dlis files within one session (script).
* Removed logging formatting from library root.
* Exposed most frequently needed objects for import from library root (``from dlis_writer import ...``).
* Explicit init arguments and docstrings for most frequently used classes.
* Saving date-time in GMT rather than 'local time'.
* Passing file header and storage unit label initialisation arguments directly to ``DLISFile``.
* General refactoring & typing fixes.

Version 0.0.7
-------------
**Equivalent (parallel) frames**

* Made it easier to add frames with the same set of channel (dataset) names, but separate data - e.g.
  two of each: DEPTH, RPM, and AMPLITUDE, coming from two separate measurements, associated with relevant frames
  (FRAME_1, FRAME_2). See ``examples/create_dlis_equivalent_frames.py``.


Version 0.0.6
-------------
**Representation codes**

* Fixed representation codes for numpy dtypes.
* Tests & improvements for utils (repr code converter, source data wrappers, etc.).


Version 0.0.5
-------------
**Cleanup**

* Some name changes, restructuring.
* Updated README.


Version 0.0.4
-------------
**All DLIS objects added**

* Exposed all types of DLIS objects (WellReferencePoint, Group, Message, etc.)
  in ``DLISFile`` through ``add_<object>`` methods (e.g. ``add_group``).


Version 0.0.3
-------------
**Instantiating ELFRObjects directly**

* Each ``EFLRObject`` (later renamed to ``EFLRItem``) can be initialised directly by calling the constructor
  of the relevant class (before they were initialised through the corresponding ``EFLR``, later renamed to ``EFLRSet``).


Version 0.0.2
-------------
**More DLIS objects**

* Added support for more objects (Zone, Splice, Axis) to the ``DLISFile``.


Version 0.0.1
-------------
**First release**

* New structure of the repository, compliant with WellID standards.
