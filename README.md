# DLIS Writer (`dliswriter`)

Welcome to DLIS Writer - an open-source Python package for writing DLIS files.

The package allows you to specify the structure, data, and metadata of your DLIS file
in a simple and flexible fashion. A minimal example is shown below.

```python
import numpy as np  # for creating mock datasets
from dliswriter import DLISFile  # the main dlis-writer object you will interact with

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

For more details about the DLIS file format and the usage of the package, please see [the documentation](https://well-id-widcdliswriter.readthedocs-hosted.com/en/latest/).

Please note that some DLIS viewers additionally restrict the expected format of the DLIS files.
In other words, if a DLIS file produced by the DLIS Writer causes issues in some of the viewers,
it might not necessarily be a DLIS Writer bug.
Some of the known compatibility issues - and ways of dealing with them - are described 
[in a dedicated section of the documentation](https://well-id-widcdliswriter.readthedocs-hosted.com/en/latest/userguide/compatibilityissues.html).


## Installation
### For end-users
DLIS Writer can be installed from PyPI:

```commandline
pip install dliswriter
```

Anaconda installation option is coming soon.

### For developers
Setting up DLIS Writer for development purposes requires: 
- Python (at least 3.10),
- Anaconda, e.g. [Miniconda](https://docs.anaconda.com/free/miniconda/),
- and [git](https://git-scm.com/).

Once these requirements are fulfilled, follow the steps below:

1. Clone the repository. From a console:
    ```commandline
    git clone https://github.com/well-id/dliswriter.git
    ```

2. Navigate to the created main project directory:
    ```commandline
    cd dliswriter
    ```

3. Create a new conda environment from the [`environment.yaml`](./environment.yaml) file and activate it:
    ```commandline
    conda env create -f .\environment.yaml
    conda activate dlis-writer
    ```
    (`dlis-writer` is the name automatically assigned to the environment.)

4. Install DLIS Writer in editable mode using `pip`:
    ```commandline
    pip install --no-build-isolation --no-deps -e .
    ```
    For explanation of the required flags, see [this issue](https://github.com/conda/conda-build/issues/4251).

5. You're good to go! For verification, you can run the tests for the package 
(still from inside the `dliswriter` directory):
    ```commandline
    pytest .
    ```

## Contributing
To contribute to the DLIS Writer, please follow the standard procedure:
1. Check out the `devel` branch: `git checkout devel`
2. Create a new branch from `devel`: `git checkout -b <your branch name>`
3. Make your changes, commit them, and push them.
4.  Create a pull request to the `devel` branch.

You might also want to have a look at our [issues log](https://github.com/well-id/dliswriter/issues).

---
## Authors
The DLIS Writer has been developed at [Well ID](https://wellid.no/) by:

* Dominika Dlugosz,
* Magne Lauritzen,
* Kamil Grunwald,
* Omer Faruk Sari.

Based on the definition of the [RP66 v1 standard](https://energistics.org/sites/default/files/RP66/V1/Toc/main.html).
