# `widc.dliswriter`

This is a repository containing the `dlis_writer` - a Python library for creating DLIS files.

For more details, please see [the documentation](https://well-id-widcdliswriter.readthedocs-hosted.com/en/latest/).

## Installation instructions
`widc.dliswriter` can be installed just like other WellID packages.

From a console:

```commandline
pip install git+https://%GIT_PAT%:x-oauth-basic@github.com/well-id/widc.dliswriter@master
```

From requirements.txt:

```commandline
git+https://${GIT_PAT}:x-oauth-basic@github.com/well-id/widc.dliswriter@master
```

## Using `widc.dliswriter`
When using the `dlis_writer`, the main class you interact with is `DLISFIle`.
An instance of this class allows you to define the structure of your DLIS and specify the data it should contain.

A minimal example is shown below:

```python
import numpy as np  # for creating mock datasets
from dlis_writer.file import DLISFile  # the main dlis-writer object you will interact with

df = DLISFile()

df.add_origin("MY-ORIGIN")  # required; can contain metadata about the well, scan procedure, etc.

# define channels with numerical data and additional information
n_rows = 100  # all datasets must have the same number of rows
ch1 = df.add_channel('DEPTH', data=np.arange(n_rows) / 10, units='m')
ch2 = df.add_channel("RPM", data=(np.arange(n_rows) % 10).astype(float))
ch3 = df.add_channel("AMPLITUDE", data=np.random.rand(n_rows, 5))

# define frame, referencing the above defined channels
main_frame = df.add_frame("MAIN-FRAME", channels=(ch1, ch2, ch3), index_type='BOREHOLE-DEPTH')

# write the data and metadata to a physical DLIS file
df.write('./new_dlis_file.DLIS')
```

## Contributing to `widc.dliswriter`
To contribute to `widc.dliswriter`, please first read the 
[Contributing](https://well-id-well-id-software-documentation.readthedocs-hosted.com/en/latest/for_developers/contribute.html) 
section of Well ID's software documentation. In short, follow these steps:

* Clone the repository to your machine: `git clone https://github.com/well-id/widc.dliswriter.git`
* Checkout the `devel` branch: `git checkout devel`
* Create a new branch: `git checkout -b <your branch name>`
* Make your changes, commit them, and push them.
* Create a pull request to the `devel` branch.

## Authors
* Dominika Dlugosz
* Kamil Grunwald
* Omer Faruk Sari

With inputs from Magne Lauritzen.

Based on the definition of the [RP66 v1 standard](https://energistics.org/sites/default/files/RP66/V1/Toc/main.html).
