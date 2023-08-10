import numpy as np
import h5py
from sys import argv
from pathlib import Path


if len(argv) > 1:
    n_points = int(float(argv[1]))
else:
    n_points = int(5e4)

fpath = Path(__file__).resolve().parent.parent/'resources/mock_data.hdf5'

if fpath.exists():
    raise RuntimeError(f"File '{fpath}' already exists. Cannot overwrite file.")

h5_file = h5py.File(fpath, 'w')
group = h5_file.create_group('contents')
group.create_dataset('time', (n_points,), float, np.arange(n_points))
group.create_dataset('depth', (n_points,), float, 10 * (np.arange(n_points) % 5))
group.create_dataset('rpm', (n_points,), float, 10 * np.sin(np.linspace(0, 1e4*np.pi, n_points)))

h5_file.flush()
h5_file.close()

print(f"Fake data with {n_points} points saved to file '{fpath}'")
