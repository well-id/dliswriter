import numpy as np
import h5py
from pathlib import Path
from argparse import ArgumentParser


def create_data_file(n_points, fpath):
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


if __name__ == '__main__':
    parser = ArgumentParser("Creating HFD5 file with mock well data")
    parser.add_argument('-n', '--n-points', help='Number of data points', type=float, default=5e4)
    parser.add_argument('-fn', '--file-name', help='Output file name')
    parser_args = parser.parse_args()

    if (file_name := parser_args.file_name) is None:
        file_name = 'mock_data.hdf5'
    if len(Path(file_name).parts) == 1 and not file_name.startswith('./'):
        file_name = Path(__file__).resolve().parent.parent / 'resources' / file_name

    create_data_file(n_points=int(parser_args.n_points), fpath=file_name)
