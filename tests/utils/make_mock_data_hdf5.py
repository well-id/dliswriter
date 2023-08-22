import numpy as np
import os
import h5py
from pathlib import Path
from argparse import ArgumentParser


def create_data(n_points: int, add_2d: bool = False) -> np.ndarray:
    data_dict = {
        'time': 0.1 * np.arange(n_points),
        'depth': 10 * (np.arange(n_points) % 5),
        'rpm': 10 * np.sin(np.linspace(0, 1e4 * np.pi, n_points))
    }

    dtype = [(key, val.dtype) for key, val in data_dict.items()]

    if add_2d:
        data_dict['image'] = (np.arange(n_points * 5) % 11).reshape(n_points, 5)
        dtype.append(('image', data_dict['image'].dtype, 5))

    data_array = np.zeros(n_points, dtype=dtype)
    for key, arr in data_dict.items():
        data_array[key] = arr

    return data_array


def create_data_file(n_points, fpath, add_2d=False):
    if fpath.exists():
        raise RuntimeError(f"File '{fpath}' already exists. Cannot overwrite file.")

    data_array = create_data(n_points, add_2d=add_2d)

    h5_file = h5py.File(fpath, 'w')
    group = h5_file.create_group('contents')

    for key in data_array.dtype.names:
        col = data_array[key]
        group.create_dataset(key, col.shape, col.dtype, col)

    h5_file.flush()
    h5_file.close()

    print(f"Fake data with {n_points} points saved to file '{fpath}'")


if __name__ == '__main__':
    parser = ArgumentParser("Creating HFD5 file with mock well data")
    parser.add_argument('-n', '--n-points', help='Number of data points', type=float, default=5e3)
    parser.add_argument('-fn', '--file-name', help='Output file name')
    parser.add_argument('--add-2d', action='store_true', default=False, help='Add 2D data entry')
    parser_args = parser.parse_args()

    if (file_name := parser_args.file_name) is None:
        file_name = 'mock_data.hdf5'
    if len(Path(file_name).parts) == 1 and not file_name.startswith('./'):
        file_name = Path(__file__).resolve().parent.parent / 'resources' / file_name
        os.makedirs(file_name.parent, exist_ok=True)

    create_data_file(n_points=int(parser_args.n_points), fpath=file_name, add_2d=parser_args.add_2d)
