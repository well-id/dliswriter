# DLIS Writer


Clone or download the repository, go to *constructor.py* if you wish to change some inputs like the output filename on **line 138**.

At this point, when you run *python constructor.py* it creates a DLIS file with only:

1. Storage Unit Label
2. File Header
3. Origin

..then using **dlisio** library, it reads the output file, and prints the file description, file header description and origin description.