import numpy as np
import pytest
import h5py

from dlis_writer.utils.source_data_wrappers import HDF5DataWrapper


@pytest.fixture(scope='session')
def mapping():
    return {'time': '/contents/time', 'rad': '/contents/image0', 'amp': '/contents/image1', 'rpm': '/contents/rpm'}


def test_basic_properties(short_reference_data_path, mapping):
    w = HDF5DataWrapper(short_reference_data_path, mapping)
    assert isinstance(w.data_source, h5py.File)
    assert w.data_source.file

    assert w.n_rows == 100
    assert isinstance(w.dtype, np.dtype)
    assert len(w.dtype) == 4


def test_creation(short_reference_data_path, mapping):
    w = HDF5DataWrapper(short_reference_data_path, mapping)
    assert w.dtype.names == ('time', 'rad', 'amp', 'rpm')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == (np.float64, (128,))
    assert w.dtype[2] == (np.float64, (128,))
    assert w.dtype[3] == np.float64


@pytest.mark.parametrize(('new_mapping', 'shapes'), (
        ({'time': 'contents/time', 'rpm': '/contents/rpm'}, [None, None]),
        ({'MD': '/contents/depth'}, [None]),
        ({'AMP': 'contents/image1', 'rpm': '/contents/rpm', 'time': 'contents/time'}, [(128,), None, None]),
        ({'AMP': 'contents/image1', 'RADIUS': '/contents/image0'}, [(128,), (128,)])
))
def test_alternative_mappings(short_reference_data_path, new_mapping, shapes):
    w = HDF5DataWrapper(short_reference_data_path, new_mapping)

    assert w.dtype.names == tuple(new_mapping.keys())
    for i in range(len(w.dtype)):
        assert w.dtype[i] == (np.float64 if shapes[i] is None else (np.float64, shapes[i]))

