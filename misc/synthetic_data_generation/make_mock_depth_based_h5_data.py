import numpy as np
import h5py
from pathlib import Path
import os


def make_image(n_rows, n_cols, divider=11):
    return (np.arange(n_rows * n_cols) % divider).reshape(n_rows, n_cols) + 5 * np.random.rand(n_rows, n_cols)


if __name__ == '__main__':
    fpath = Path(__file__).parent/'tmp_data/mock_depth_amplitude_radius.hdf5'

    depth_min = 2500
    depth_span = 100
    depth_res = 0.1

    n_points = int(depth_span // depth_res + 1)
    n_cols = 128

    if fpath.exists():
        os.remove(fpath)

    h5_file = h5py.File(fpath, 'w')
    try:
        group = h5_file.create_group('contents')
        group.create_dataset('depth', (n_points,), data=depth_min + depth_res * np.arange(n_points))
        group.create_dataset('amplitude', (n_points, n_cols), data=make_image(n_points, n_cols, divider=n_cols-1))
        group.create_dataset('radius', (n_points, n_cols), data=make_image(n_points, n_cols, divider=31))
    except Exception as exc:
        h5_file.flush()
        h5_file.close()
        raise exc
    else:
        h5_file.flush()
        h5_file.close()

    print(f"Fake data with {n_points} points saved to file '{fpath}'")
