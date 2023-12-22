import numpy as np
import pytest

from dlis_writer.utils.source_data_wrappers import NumpyDataWrapper


@pytest.fixture
def data():
    data_types = [
        ('depth', float),
        ('rpm', int),
        ('amplitude', np.float16, 128),
        ('radius', np.int64, 20)
    ]

    n = 100
    arr = np.empty(n, dtype=np.dtype(data_types))
    arr['depth'] = np.arange(n) * 0.01
    arr['rpm'] = np.random.randint(size=n, low=5, high=10)
    arr['amplitude'] = np.random.rand(n, 128)
    arr['radius'] = (10 * np.random.rand(n, 20)).astype(int)

    return arr


def test_creation(data):
    w = NumpyDataWrapper(data)

    assert w.dtype == data.dtype
    assert w.dtype.names == ('depth', 'rpm', 'amplitude', 'radius')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float16, (128,))
    assert w.dtype[3] == (np.int64, (20,))


def test_creation_with_mapping(data):
    w = NumpyDataWrapper(data, mapping={'DPTH': 'depth', 'RPM': 'rpm', 'AMP': 'amplitude', 'RAD': 'radius'})

    assert w.dtype.names == ('DPTH', 'RPM', 'AMP', 'RAD')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float16, (128,))
    assert w.dtype[3] == (np.int64, (20,))


def test_creation_with_mapping_different_order(data):
    w = NumpyDataWrapper(data, mapping={'RAD': 'radius', 'AMP': 'amplitude', 'RPM': 'rpm', 'DPTH': 'depth'})

    assert w.dtype.names == ('RAD', 'AMP', 'RPM', 'DPTH')
    assert w.dtype[3] == np.float64
    assert w.dtype[2] == np.int32
    assert w.dtype[1] == (np.float16, (128,))
    assert w.dtype[0] == (np.int64, (20,))


def test_creation_with_mapping_omitting_dsets(data):
    w = NumpyDataWrapper(data, mapping={'AMP': 'amplitude', 'DPTH': 'depth'})

    assert w.dtype.names == ('AMP', 'DPTH')
    assert w.dtype[1] == np.float64
    assert w.dtype[0] == (np.float16, (128,))


@pytest.mark.parametrize(('known_dtypes', 'dtype_check'), (
        ({'depth': np.float32, 'rpm': np.float64}, (np.float32, np.float64, np.float16, np.int64)),
        ({'rpm': np.int64}, (np.float64, np.int64, np.float16, np.int64)),
        ({'radius': np.float32, 'amplitude': np.float64}, (np.float64, np.int32, np.float64, np.float32))
))
def test_creation_with_known_dtypes(data, known_dtypes, dtype_check):
    w = NumpyDataWrapper(data, known_dtypes=known_dtypes)

    assert w.dtype[0] == dtype_check[0]
    assert w.dtype[1] == dtype_check[1]
    assert w.dtype[2] == (dtype_check[2], (128,))
    assert w.dtype[3] == (dtype_check[3], (20,))


def test_creation_with_known_dtypes_and_mapping(data):
    w = NumpyDataWrapper(
        data,
        mapping={'RAD': 'radius', 'AMP': 'amplitude', 'RPM': 'rpm'},
        known_dtypes={'AMP': np.int32, 'RPM': np.float16}
    )

    assert w.dtype.names == ('RAD', 'AMP', 'RPM')
    assert w.dtype[0] == (np.int64, (20,))  # radius
    assert w.dtype[1] == (np.int32, (128,))  # amplitude
    assert w.dtype[2] == np.float16  # rpm
