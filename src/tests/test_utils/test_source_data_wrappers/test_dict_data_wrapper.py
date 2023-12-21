import numpy as np
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


def test_creation_without_mapping(data):
    w = DictDataWrapper(data)

    assert w.dtype.names == ('depth', 'rpm', 'amplitude')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int_
    assert w.dtype[2] == (np.float16, (128,))


def test_creation_with_mapping(data):
    w = DictDataWrapper(data, mapping={'MD': 'depth', 'RPM': 'rpm', 'AMP': 'amplitude'})

    assert w.dtype.names == ('MD', 'RPM', 'AMP')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int_
    assert w.dtype[2] == (np.float16, (128,))
