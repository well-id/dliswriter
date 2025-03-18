import numpy as np
from pathlib import Path
import pytest
import logging
from typing import Union, Any

from dliswriter.utils.source_data_wrappers import DictDataWrapper, SourceDataWrapper


source_data_type = dict[str, np.ndarray]


@pytest.fixture
def data() -> source_data_type:
    """Mock source data for dict data wrapper."""

    n = 100
    d = {
        'depth': np.arange(n) * 0.1,
        'rpm': (10 * np.random.rand(n)).astype(np.int32),
        'amplitude': np.random.rand(n, 128).astype(np.float32),
    }

    return d


def test_basic_properties(data: source_data_type) -> None:
    """Check basic attributes of a dict data wrapper instance created with default settings."""

    w = DictDataWrapper(data)
    assert w.data_source is data
    assert w.n_rows == 100
    assert isinstance(w.dtype, np.dtype)
    assert isinstance(w.dtype.names, tuple)
    assert len(w.dtype.names) == 3


def test_creation_without_mapping(data: source_data_type) -> None:
    """Check that a dict wrapper with default mapping is created correctly."""

    w = DictDataWrapper(data)

    assert w.dtype.names == ('depth', 'rpm', 'amplitude')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float32, (128,))


def test_creation_with_mapping(data: source_data_type) -> None:
    """Check that a dict wrapper with alternative mapping is created correctly."""

    w = DictDataWrapper(data, mapping={'MD': 'depth', 'RPM': 'rpm', 'AMP': 'amplitude'})

    assert w.dtype.names == ('MD', 'RPM', 'AMP')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float32, (128,))


def test_creation_with_mapping_omitting_dsets(data: source_data_type) -> None:
    """Test creating a dict wrapper which omits some of the datasets found in the source data."""

    w = DictDataWrapper(data, mapping={'MD': 'depth', 'AMP': 'amplitude'})  # no rpm

    assert w.dtype.names == ('MD', 'AMP')
    assert w.dtype[0] == np.float64
    assert w.dtype[1] == (np.float32, (128,))


def test_creation_with_known_dtypes(data: source_data_type) -> None:
    """Test creating a dict wrapper with some data types explicitly provided."""

    w = DictDataWrapper(data, known_dtypes={'depth': np.float32, 'rpm': np.float64})

    assert w.dtype[0] == np.float32
    assert w.dtype[1] == np.float64
    assert w.dtype[2] == (np.float32, (128,))


def test_creation_with_known_dtypes_and_mapping(data: source_data_type) -> None:
    """Test creating a dict wrapper with alternative mapping and provided (matching) data types."""

    w = DictDataWrapper(
        data,
        mapping={'MD': 'depth', 'RPM': 'rpm', 'AMP': 'amplitude'},
        known_dtypes={'MD': np.float32, 'AMP': np.float64}  # names the same as keys of the mapping dict
    )

    assert w.dtype[0] == np.float32
    assert w.dtype[1] == np.int32
    assert w.dtype[2] == (np.float64, (128,))


@pytest.mark.parametrize('data_dict', (np.arange(12), [10, 20, 30, 40], 'path/to/something'))
def test_type_error_if_not_dict(data_dict: Any) -> None:
    """Check that a type error is raised if source data are not a dict."""

    with pytest.raises(TypeError, match="Expected a dictionary.*"):
        DictDataWrapper(data_dict)


@pytest.mark.parametrize('radius', (3, object(), 'path/to/something', (1, 2, 4.5), list(range(100))))
def test_type_error_if_not_numpy(data: source_data_type, radius: Any) -> None:
    """Check that a type error is raised if values of the data dict are anything other than a numpy.ndarray."""

    data2 = data | {'radius': radius}

    with pytest.raises(TypeError, match='Dict values must be numpy arrays.*'):
        DictDataWrapper(data2)


@pytest.mark.parametrize('key', (3, Path(__file__).resolve(), (1, 2, 3)))
def test_type_error_if_key_not_str(data: source_data_type, key: Any) -> None:
    """Check that a type error is raised if keys of the data dictionary are not strings."""

    data2 = data | {key: np.random.rand(100)}

    with pytest.raises(TypeError, match="Source dictionary keys must be strings.*"):
        DictDataWrapper(data2)


def test_creation_from_superclass(data: source_data_type) -> None:
    """Check that a dict wrapper is created from SourceDataWrapper.make_wrapper if the source data are a dict."""

    w = SourceDataWrapper.make_wrapper(data)
    assert isinstance(w, DictDataWrapper)


@pytest.mark.parametrize(('from_idx', 'to_idx', 'n_rows'), ((0, 10, 10), (60, 63, 3), (92, None, 8)))
def test_creation_with_from_and_to_idx(data: source_data_type, from_idx: int, to_idx: Union[int, None],
                                       n_rows: int) -> None:
    """Check creating a dict wrapper with specified from- and to-indices in the original data."""

    w = DictDataWrapper(data, from_idx=from_idx, to_idx=to_idx)
    assert w.n_rows == n_rows


@pytest.mark.parametrize(('start', 'stop'), ((0, 10), (1, 2), (3, 3), (3, 17), (61, 100)))
def test_load_chunk(data: source_data_type, start: int, stop: int) -> None:
    """Test loading a data chunk from a dict wrapper."""

    w = DictDataWrapper(data)
    chunk = w.load_chunk(start, stop)

    assert chunk.size == stop - start
    assert chunk.dtype == w.dtype
    assert (chunk['depth'] == data['depth'][start:stop]).all()
    assert (chunk['rpm'] == data['rpm'][start:stop]).all()
    assert (chunk['amplitude'] == data['amplitude'][start:stop]).all()


@pytest.mark.parametrize('start', (0, 10, 99, 100))
def test_load_chunk_until_end(data: source_data_type, start: int) -> None:
    """Test loading a data chunk from a specified point until the end."""

    w = DictDataWrapper(data)
    chunk = w.load_chunk(start, stop=None)

    assert chunk.size == 100 - start
    assert chunk.dtype == w.dtype
    assert (chunk['depth'] == data['depth'][start:]).all()
    assert (chunk['rpm'] == data['rpm'][start:]).all()
    assert (chunk['amplitude'] == data['amplitude'][start:]).all()


@pytest.mark.parametrize(('start', 'stop'), ((0, 101), (99, 1000)))
def test_load_chunk_stop_too_large(data: source_data_type, start: int, stop: int) -> None:
    """Check that a ValueError is raised if the specified chunk stop index is too large."""

    w = DictDataWrapper(data)

    with pytest.raises(ValueError, match=f"Cannot load chunk up to row {stop}.*"):
        w.load_chunk(start, stop)


@pytest.mark.parametrize('start', (101, 1210))
def test_load_chunk_start_too_large(data: source_data_type, start: int) -> None:
    """Check that a ValueError is raised if the specified chunk start index is too large."""

    w = DictDataWrapper(data)

    with pytest.raises(ValueError, match=f"Cannot load chunk from row {start}.*"):
        w.load_chunk(start, None)


@pytest.mark.parametrize(('start', 'stop'), ((10, 9), (90, 10)))
def test_load_chunk_start_larger_than_stop(data: source_data_type, start: int, stop: int) -> None:
    """Check that a ValueError is raised if the specified chunk start is larger than the stop."""

    w = DictDataWrapper(data)

    with pytest.raises(ValueError, match="Stop row cannot be smaller than start row.*"):
        w.load_chunk(start, stop)


@pytest.mark.parametrize(('start', 'from_idx'), ((60, 50), (10, 92), (91, 10)))
def test_load_chunk_start_too_large_with_from_idx(data: source_data_type, start: int, from_idx: int) -> None:
    """Check that a ValueError is raised if the specified chunk start index is too large with a from_idx specified."""

    w = DictDataWrapper(data, from_idx=from_idx)

    with pytest.raises(ValueError, match=f"Cannot load chunk from row {start}.*"):
        w.load_chunk(start, None)


@pytest.mark.parametrize(('stop', 'from_idx'), ((60, 50), (10, 92), (91, 10)))
def test_load_chunk_stop_too_large_with_from_idx(data: source_data_type, stop: int, from_idx: int) -> None:
    """Check that a ValueError is raised if the specified chunk stop index is too large with a from_idx specified."""

    w = DictDataWrapper(data, from_idx=from_idx)

    with pytest.raises(ValueError, match=f"Cannot load chunk up to row {stop}.*"):
        w.load_chunk(0, stop)


@pytest.mark.parametrize(('start', 'stop', 'from_idx', 'to_idx'), (
        (0, 10, 20, 40),
        (1, 2, 90, 92),
        (3, 3, 28, 55),
        (3, 17, 83, None)
))
def test_load_chunk_with_from_and_to_idx(data: source_data_type, start: int, stop: int, from_idx: int,
                                         to_idx: Union[int, None]) -> None:
    """Test loading a data chunk if from_idx and to_idx were specified."""

    w = DictDataWrapper(data, from_idx=from_idx, to_idx=to_idx)
    chunk = w.load_chunk(start, stop)

    assert chunk.size == stop - start
    assert chunk.dtype == w.dtype
    assert (chunk['depth'] == data['depth'][from_idx+start:from_idx+stop]).all()
    assert (chunk['rpm'] == data['rpm'][from_idx+start:from_idx+stop]).all()
    assert (chunk['amplitude'] == data['amplitude'][from_idx+start:from_idx+stop]).all()


@pytest.mark.parametrize(('start', 'from_idx', 'to_idx'), (
        (0, 20, 40),
        (1, 90, 92),
        (3, 28, 55),
        (3, 83, None)
))
def test_load_chunk_until_end_with_from_and_to_idx(data: source_data_type, start: int, from_idx: int,
                                                   to_idx: Union[int, None]) -> None:
    """Test loading a data chunk until the end if from_idx and to_idx were specified."""

    w = DictDataWrapper(data, from_idx=from_idx, to_idx=to_idx)
    chunk = w.load_chunk(start, stop=None)

    assert chunk.size == ((to_idx or 100) - from_idx) - start
    assert chunk.dtype == w.dtype
    assert (chunk['depth'] == data['depth'][from_idx+start:to_idx]).all()
    assert (chunk['rpm'] == data['rpm'][from_idx+start:to_idx]).all()
    assert (chunk['amplitude'] == data['amplitude'][from_idx+start:to_idx]).all()


def test_load_chunk_alternative_mapping(data: source_data_type) -> None:
    """Test loading a data chunk if alternative data names mapping was provided."""

    w = DictDataWrapper(data, mapping={'AMP': 'amplitude', 'MD': 'depth'})  # no rpm, switched order
    chunk = w.load_chunk(10, 20)

    assert chunk.size == 10
    assert chunk.dtype.names == ('AMP', 'MD')
    assert chunk.dtype == w.dtype

    assert (chunk['AMP'] == data['amplitude'][10:20]).all()
    assert (chunk['MD'] == data['depth'][10:20]).all()


@pytest.mark.parametrize(("from_idx", "to_idx", "n_rows"), ((0, None, 100), (20, 60, 40)))
def test_chunked_generator_all_rows(data: source_data_type, caplog: pytest.LogCaptureFixture, from_idx: int,
                                    to_idx: Union[int, None], n_rows: int) -> None:
    """Test loading data in a single chunk."""

    w = DictDataWrapper(data, from_idx=from_idx, to_idx=to_idx)

    with caplog.at_level(logging.DEBUG, logger='dliswriter'):
        gen = w.make_chunked_generator(chunk_rows=None)
        rows = list(gen)

    assert f"Data will be loaded in a single chunk of {n_rows}" in caplog.text
    assert "Loading chunk 1/1" in caplog.text

    assert len(rows) == n_rows

    assert rows[0]['depth'] == data['depth'][from_idx:to_idx][0]
    assert (rows[17]['amplitude'] == data['amplitude'][from_idx:to_idx][17]).all()
    assert rows[-2]['rpm'] == data['rpm'][from_idx:to_idx][n_rows-2]


@pytest.mark.parametrize(("chunk_rows", "n_chunks"), ((10, 10), (25, 4)))
def test_chunked_generator_full_chunks(data: source_data_type, caplog: pytest.LogCaptureFixture, chunk_rows: int,
                                       n_chunks: int) -> None:
    """Test loading data in several full chunks."""

    w = DictDataWrapper(data)

    with caplog.at_level(logging.DEBUG, logger='dliswriter'):
        gen = w.make_chunked_generator(chunk_rows=chunk_rows)
        rows = list(gen)

    assert f"Data will be loaded in {n_chunks} chunk(s) of {chunk_rows} rows" in caplog.text
    assert "plus a last, smaller chunk" not in caplog.text

    for i in range(n_chunks):
        assert f"Loading chunk {i+1}/{n_chunks}" in caplog.text

    assert len(rows) == 100

    assert rows[15]['depth'] == data['depth'][15]
    assert (rows[0]['amplitude'] == data['amplitude'][0]).all()
    assert rows[3]['rpm'] == data['rpm'][3]


@pytest.mark.parametrize(("chunk_rows", "n_full_chunks", "remainder_rows"), ((15, 6, 10), (40, 2, 20), (60, 1, 40)))
def test_chunked_generator_remainder_chunk(data: source_data_type, caplog: pytest.LogCaptureFixture, chunk_rows: int,
                                           n_full_chunks: int, remainder_rows: int) -> None:
    """Test loading data in several full and last half-full chunk."""

    w = DictDataWrapper(data)

    with caplog.at_level(logging.DEBUG, logger='dliswriter'):
        gen = w.make_chunked_generator(chunk_rows=chunk_rows)
        rows = list(gen)

    assert f"Data will be loaded in {n_full_chunks} chunk(s) of {chunk_rows} rows" in caplog.text
    assert f"plus a last, smaller chunk of {remainder_rows} rows" in caplog.text

    for i in range(n_full_chunks + 1):
        assert f"Loading chunk {i+1}/{n_full_chunks + 1}" in caplog.text

    assert len(rows) == 100

    assert rows[80]['depth'] == data['depth'][80]
    assert (rows[2]['amplitude'] == data['amplitude'][2]).all()
    assert rows[24]['rpm'] == data['rpm'][24]


@pytest.mark.parametrize(("from_idx", "to_idx"), ((0, None), (10, 30)))
def test_getitem_default_mapping(data: source_data_type, from_idx: int, to_idx: Union[int, None]) -> None:
    """Test the __getitem__ functionality for a dict wrapper created with default mapping."""

    w = DictDataWrapper(data, from_idx=from_idx, to_idx=to_idx)

    for key in ('depth', 'amplitude', 'rpm'):
        assert isinstance(w[key], np.ndarray)

    assert (w['depth'] == data['depth'][from_idx:to_idx]).all()
    assert (w['amplitude'] == data['amplitude'][from_idx:to_idx]).all()
    assert (w['rpm'] == data['rpm'][from_idx:to_idx]).all()


@pytest.mark.parametrize(("from_idx", "to_idx"), ((0, None), (20, 21)))
def test_getitem_alternative_mapping(data: source_data_type, from_idx: int, to_idx: Union[int, None]) -> None:
    """Test the __getitem__ functionality for a dict wrapper created with alternative mapping."""

    w = DictDataWrapper(data, from_idx=from_idx, to_idx=to_idx, mapping={'MD': 'depth', 'RPM': 'rpm'})

    for key in ('MD', 'RPM'):
        assert isinstance(w[key], np.ndarray)

    assert (w['MD'] == data['depth'][from_idx:to_idx]).all()
    assert (w['RPM'] == data['rpm'][from_idx:to_idx]).all()

    for key in ('depth', 'rpm', 'amplitude'):
        with pytest.raises(ValueError, match=f"No dataset '{key}' found in the source data"):
            w[key]
