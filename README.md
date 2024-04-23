![Licence](https://img.shields.io/github/license/well-id/dliswriter)
![Test coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/the-mysh/8ec74eae558f3a7793622f6469064b73/raw/test_coverage_badge.json)
[![Linting and testing](https://github.com/well-id/dliswriter/actions/workflows/LintAndTest.yml/badge.svg)](https://github.com/well-id/dliswriter/actions/workflows/LintAndTest.yml)
[![Documentation Status](https://readthedocs.com/projects/well-id-widcdliswriter/badge/?version=latest)](https://well-id-widcdliswriter.readthedocs-hosted.com/?badge=latest)
![Latest PyPI release](https://img.shields.io/pypi/v/dliswriter)

# `dliswriter`

<p align="center" width="100%">
    <img width="15%" src="logo.png">
</p>


Welcome to `dliswriter` - an open-source Python package for writing DLIS files.

The package allows you to specify the structure, data, and metadata of your DLIS file
in a simple and flexible fashion. A minimal example is shown below.

```python
import numpy as np  # for creating mock datasets
from dliswriter import DLISFile, enums

df = DLISFile()

df.add_origin("MY-ORIGIN")  # required; can contain metadata about the well, scan procedure, etc.

# define channels with numerical data and additional information
n_rows = 100  # all datasets must have the same number of rows
ch1 = df.add_channel('DEPTH', data=np.linspace(0, 10, n_rows), units=enums.Unit.METER)
ch2 = df.add_channel("RPM", data=np.arange(n_rows) % 10)
ch3 = df.add_channel("AMPLITUDE", data=np.random.rand(n_rows, 5))

# define frame, referencing the above defined channels
main_frame = df.add_frame("MAIN-FRAME", channels=(ch1, ch2, ch3), index_type=enums.FrameIndexType.BOREHOLE_DEPTH)

# write the data and metadata to a physical DLIS file
df.write('./new_dlis_file.DLIS')
```

For more details about the DLIS file format and using `dliswriter`, please see [the documentation](https://well-id-widcdliswriter.readthedocs-hosted.com/index.html).

### Performance
According to our rough measurements, the file writing time seems to be pretty much linearly dependent on the 
amount of data, in particular the number of rows. There is also some dependency on the dimensionality 
of the data - e.g a single image (2D dataset) with 1000 columns will write about 20% faster 
than 10 images of 100 columns each. A rough estimate of the writing speed is about 20M `float64` values per second
(measured on an x64-based PC with Intel Core i9-8950HK with MS Windows 11 and Python 3.9.19).

The performance may be further tuned by adjusting the `input_chunk_size` and `output_chunk_size` of the writer
(see [this example](./examples/create_synth_dlis_variable_data.py)). The former limits how much of the input 
data are loaded to memory at a time; the latter denotes the number of output bytes kept in memory before each partial 
file write action. The optimal values depend on the hardware/software configuration and the characteristics of the data
(number and dimensionality of the datasets), but the defaults should in general be a good starting point.


### Compatibility notes

Please note that some DLIS viewer applications are not fully compliant with the DLIS standard.
If a DLIS file produced by `dliswriter` causes issues in some of the viewers, it might not necessarily 
be a `dliswriter` bug.
Some of the known compatibility issues - and ways of dealing with them - are described 
[in a dedicated section of the documentation](https://well-id-widcdliswriter.readthedocs-hosted.com/userguide/compatibilityissues.html).
If you run into problems not covered by the documentation, please open a new [issue](https://github.com/well-id/dliswriter/issues).


## Installation
`dliswriter` can be installed from PyPI:

```commandline
pip install dliswriter
```

Anaconda installation option is coming soon.

### For developers
Setting up `dliswriter` for development purposes requires: 
- Python (at least 3.10)
- Anaconda, e.g. [Miniconda](https://docs.anaconda.com/free/miniconda/)
- [git](https://git-scm.com/)

Once these requirements are fulfilled, follow the steps below:

1. Clone the repository and enter it. From a console:
    ```commandline
    git clone https://github.com/well-id/dliswriter.git
    cd dliswriter
    ```

2. Create the `dlis-writer` environment from the [`environment.yaml`](./environment.yaml) file and activate it:
    ```commandline
    conda env create -f environment.yaml
    conda activate dlis-writer
    ```

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
To contribute to the `dliswriter`, please follow this procedure:
1. Check out the `devel` branch: `git checkout devel`
2. Create a new branch from `devel`: `git checkout -b <your branch name>`
3. Make your changes, commit them, and push them
4.  Create a pull request to the `devel` branch

You might also want to have a look at our [issues log](https://github.com/well-id/dliswriter/issues).

---
## Authors
`dliswriter` has been developed at [Well ID](https://wellid.no/) by:

* Dominika Dlugosz
* Magne Lauritzen
* Kamil Grunwald
* Omer Faruk Sari

Based on the definition of the [RP66 v1 standard](https://energistics.org/sites/default/files/RP66/V1/Toc/main.html).
