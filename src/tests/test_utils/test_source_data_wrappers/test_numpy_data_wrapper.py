import numpy as np
import pytest
from typing import Union, Any

from dlis_writer.utils.source_data_wrappers import NumpyDataWrapper, SourceDataWrapper


@pytest.fixture
def dtype() -> np.dtype:
    data_types = [
        ('depth', float),
        ('rpm', int),
        ('amplitude', np.float32, 128),
        ('radius', np.int32, 20)
    ]
    return np.dtype(data_types)


def test_basic_properties(data: np.ndarray) -> None:
    w = NumpyDataWrapper(data)
    assert w.data_source is data
    assert w.n_rows == 50
    assert isinstance(w.dtype, np.dtype)
    assert isinstance(w.dtype.names, tuple)
    assert len(w.dtype.names) == 4


@pytest.fixture
def data(dtype: np.dtype) -> np.ndarray:
    n = 50
    arr = np.empty(n, dtype=dtype)
    arr['depth'] = np.arange(n) * 0.01
    arr['rpm'] = np.random.randint(size=n, low=5, high=10)
    arr['amplitude'] = np.random.rand(n, 128)
    arr['radius'] = (10 * np.random.rand(n, 20)).astype(int)

    return arr


def test_creation(data: np.ndarray) -> None:
    w = NumpyDataWrapper(data)

    assert w.dtype == data.dtype
    assert w.dtype.names == ('depth', 'rpm', 'amplitude', 'radius')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float32, (128,))
    assert w.dtype[3] == (np.int32, (20,))


def test_creation_with_mapping(data: np.ndarray) -> None:
    w = NumpyDataWrapper(data, mapping={'DPTH': 'depth', 'RPM': 'rpm', 'AMP': 'amplitude', 'RAD': 'radius'})

    assert w.dtype.names == ('DPTH', 'RPM', 'AMP', 'RAD')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float32, (128,))
    assert w.dtype[3] == (np.int32, (20,))


def test_creation_with_mapping_different_order(data: np.ndarray) -> None:
    w = NumpyDataWrapper(data, mapping={'RAD': 'radius', 'AMP': 'amplitude', 'RPM': 'rpm', 'DPTH': 'depth'})

    assert w.dtype.names == ('RAD', 'AMP', 'RPM', 'DPTH')
    assert w.dtype[3] == np.float64
    assert w.dtype[2] == np.int32
    assert w.dtype[1] == (np.float32, (128,))
    assert w.dtype[0] == (np.int32, (20,))


def test_creation_with_mapping_omitting_dsets(data: np.ndarray) -> None:
    w = NumpyDataWrapper(data, mapping={'AMP': 'amplitude', 'DPTH': 'depth'})

    assert w.dtype.names == ('AMP', 'DPTH')
    assert w.dtype[1] == np.float64
    assert w.dtype[0] == (np.float32, (128,))


@pytest.mark.parametrize(('known_dtypes', 'dtype_check'), (
        ({'depth': np.float32, 'rpm': np.float64}, (np.float32, np.float64, np.float32, np.int32)),
        ({'rpm': np.int32}, (np.float64, np.int32, np.float32, np.int32)),
        ({'radius': np.float32, 'amplitude': np.float64}, (np.float64, np.int32, np.float64, np.float32))
))
def test_creation_with_known_dtypes(data: np.ndarray, known_dtypes: dict, dtype_check: tuple) -> None:
    w = NumpyDataWrapper(data, known_dtypes=known_dtypes)

    assert w.dtype[0] == dtype_check[0]
    assert w.dtype[1] == dtype_check[1]
    assert w.dtype[2] == (dtype_check[2], (128,))
    assert w.dtype[3] == (dtype_check[3], (20,))


def test_creation_with_known_dtypes_and_mapping(data: np.ndarray) -> None:
    w = NumpyDataWrapper(
        data,
        mapping={'RAD': 'radius', 'AMP': 'amplitude', 'RPM': 'rpm'},
        known_dtypes={'AMP': np.int32, 'RPM': np.float32}
    )

    assert w.dtype.names == ('RAD', 'AMP', 'RPM')
    assert w.dtype[0] == (np.int32, (20,))  # radius
    assert w.dtype[1] == (np.int32, (128,))  # amplitude
    assert w.dtype[2] == np.float32  # rpm


@pytest.mark.parametrize('dat', (
        '/path/to/file.npz',
        {'depth': np.arange(50), 'amplitude': np.random.rand(50, 128)},
        [1, 2, 3, 4, 5]
))
def test_type_error_if_not_numpy(dat: Any) -> None:
    with pytest.raises(TypeError, match="Expected a numpy.ndarray.*"):
        NumpyDataWrapper(dat)


@pytest.mark.parametrize('dat', (
        np.arange(12),
        np.random.rand(50),
        np.random.rand(150)
))
def test_value_error_if_not_structured_numpy(dat: np.ndarray) -> None:
    with pytest.raises(ValueError, match="Input must be a structured numpy array"):
        NumpyDataWrapper(dat)


@pytest.mark.parametrize('dat', (
        np.random.rand(50, 150),
        np.random.rand(150, 50)
))
def test_value_error_if_array_not_1d(dat: np.ndarray) -> None:
    with pytest.raises(ValueError, match="Source array must be 1-dimensional"):
        NumpyDataWrapper(dat)


@pytest.mark.parametrize('shape', ((10, 20), (1, 50), (12, 17, 19)))
def test_value_error_if_structured_array_not_1d(dtype: np.dtype, shape: tuple) -> None:
    with pytest.raises(ValueError, match="Source array must be 1-dimensional"):
        NumpyDataWrapper(np.ones(shape, dtype=dtype))


def test_creation_from_superclass(data: np.ndarray) -> None:
    w = SourceDataWrapper.make_wrapper(data)
    assert isinstance(w, NumpyDataWrapper)


@pytest.mark.parametrize(('from_idx', 'to_idx', 'n_rows'), ((0, 20, 20), (32, None, 18), (12, 25, 13)))
def test_creation_with_from_and_to_idx(data: np.ndarray, from_idx: int, to_idx: Union[int, None], n_rows: int) -> None:
    w = NumpyDataWrapper(data, from_idx=from_idx, to_idx=to_idx)
    assert w.n_rows == n_rows


@pytest.mark.parametrize(('start', 'stop'), ((0, 10), (1, 2), (3, 3), (3, 17)))
def test_load_chunk(data: np.ndarray, start: int, stop: int) -> None:
    w = NumpyDataWrapper(data)
    chunk = w.load_chunk(start, stop)

    assert chunk.size == stop - start
    assert chunk.dtype == w.dtype
    assert (chunk['depth'] == data['depth'][start:stop]).all()
    assert (chunk['rpm'] == data['rpm'][start:stop]).all()
    assert (chunk['amplitude'] == data['amplitude'][start:stop]).all()


@pytest.mark.parametrize(('start', 'stop'), ((30, 45), (11, 12)))
def test_load_chunk_alternative_mapping(data: np.ndarray, start: int, stop: int) -> None:
    w = NumpyDataWrapper(data, mapping={'RPM': 'rpm', 'MD': 'depth'})  # no amplitude, switched order
    chunk = w.load_chunk(start, stop)

    assert chunk.size == stop - start
    assert chunk.dtype.names == ('RPM', 'MD')
    assert chunk.dtype == w.dtype

    assert (chunk['RPM'] == data['rpm'][start:stop]).all()
    assert (chunk['MD'] == data['depth'][start:stop]).all()


@pytest.mark.parametrize(("from_idx", "to_idx"), ((0, 30), (40, None)))
def test_getitem_default_mapping(data: np.ndarray, from_idx: int, to_idx: Union[int, None]) -> None:
    w = NumpyDataWrapper(data, from_idx=from_idx, to_idx=to_idx)

    for key in ('depth', 'amplitude', 'rpm', 'radius'):
        assert isinstance(w[key], np.ndarray)

    assert (w['depth'] == data['depth'][from_idx:to_idx]).all()
    assert (w['amplitude'] == data['amplitude'][from_idx:to_idx]).all()
    assert (w['rpm'] == data['rpm'][from_idx:to_idx]).all()
    assert (w['radius'] == data['radius'][from_idx:to_idx]).all()


@pytest.mark.parametrize(("from_idx", "to_idx"), ((1, None), (11, 12)))
def test_getitem_alternative_mapping(data: np.ndarray, from_idx: int, to_idx: Union[int, None]) -> None:
    w = NumpyDataWrapper(data, from_idx=from_idx, to_idx=to_idx, mapping={'AMP': 'amplitude', 'RAD': 'radius'})

    for key in ('AMP', 'RAD'):
        assert isinstance(w[key], np.ndarray)

    assert (w['AMP'] == data['amplitude'][from_idx:to_idx]).all()
    assert (w['RAD'] == data['radius'][from_idx:to_idx]).all()

    for key in ('depth', 'rpm', 'amplitude', 'radius'):
        with pytest.raises(ValueError, match=f"No dataset '{key}' found in the source data"):
            w[key]
