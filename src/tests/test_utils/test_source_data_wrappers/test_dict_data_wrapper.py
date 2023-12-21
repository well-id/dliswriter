import numpy as np
from pathlib import Path
import pytest

from dlis_writer.utils.source_data_wrappers import DictDataWrapper


@pytest.fixture
def data():
    n = 100
    d = {
        'depth': np.arange(n) * 0.1,
        'rpm': (10 * np.random.rand(n)).astype(int),
        'amplitude': np.random.rand(n, 128).astype(np.float16)
    }

    return d


def test_basic_properties(data):
    w = DictDataWrapper(data)
    assert w.data_source is data
    assert w.n_rows == 100
    assert isinstance(w.dtype, np.dtype)
    assert len(w.dtype) == 3


def test_creation_without_mapping(data):
    w = DictDataWrapper(data)

    assert w.dtype.names == ('depth', 'rpm', 'amplitude')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float16, (128,))


def test_creation_with_mapping(data):
    w = DictDataWrapper(data, mapping={'MD': 'depth', 'RPM': 'rpm', 'AMP': 'amplitude'})

    assert w.dtype.names == ('MD', 'RPM', 'AMP')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float16, (128,))


def test_creation_with_known_dtypes(data):
    w = DictDataWrapper(data, known_dtypes={'depth': np.float32, 'rpm': np.float64})

    assert w.dtype[0] == np.float32
    assert w.dtype[1] == np.float64
    assert w.dtype[2] == (np.float16, (128,))


def test_creation_with_known_dtypes_and_mapping(data):
    w = DictDataWrapper(
        data,
        mapping={'MD': 'depth', 'RPM': 'rpm', 'AMP': 'amplitude'},
        known_dtypes={'MD': np.float16, 'AMP': np.float64}  # names the same as keys of the mapping dict
    )

    assert w.dtype[0] == np.float16
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float64, (128,))


@pytest.mark.parametrize('data_dict', (np.arange(12), [10, 20, 30, 40], 'path/to/something'))
def test_type_error_if_not_dict(data_dict):
    with pytest.raises(TypeError, match="Expected a dictionary.*"):
        DictDataWrapper(data_dict)


@pytest.mark.parametrize('radius', (3, object(), 'path/to/something', (1, 2, 4.5), list(range(100))))
def test_type_error_if_not_numpy(data, radius):
    data2 = data | {'radius': radius}

    with pytest.raises(TypeError, match='Dict values must be numpy arrays.*'):
        DictDataWrapper(data2)


@pytest.mark.parametrize('key', (3, Path(__file__).resolve(), (1, 2, 3)))
def test_type_error_if_key_not_str(data, key):
    data2 = data | {key: np.random.rand(100)}

    with pytest.raises(TypeError, match="Source dictionary keys must be strings.*"):
        DictDataWrapper(data2)
