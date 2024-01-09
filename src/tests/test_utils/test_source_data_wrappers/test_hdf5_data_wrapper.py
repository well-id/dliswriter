import numpy as np
import pytest
import h5py

from dlis_writer.utils.source_data_wrappers import HDF5DataWrapper, SourceDataWrapper


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


@pytest.mark.parametrize(('known_dtypes', 'dtype_check'), (
        ({'time': np.float32, 'rpm': np.float16}, (np.float32, np.float64, np.float64, np.float16)),
        ({'rpm': np.int64}, (np.float64, np.float64, np.float64, np.int64)),
        ({'rad': np.float32, 'amp': np.int64}, (np.float64, np.float32, np.int64, np.float64))
))
def test_creation_with_known_dtypes(short_reference_data_path, known_dtypes, dtype_check, mapping):
    w = HDF5DataWrapper(short_reference_data_path, known_dtypes=known_dtypes, mapping=mapping)

    assert w.dtype[0] == dtype_check[0]
    assert w.dtype[1] == (dtype_check[1], (128,))
    assert w.dtype[2] == (dtype_check[2], (128,))
    assert w.dtype[3] == dtype_check[3]


def test_creation_from_superclass(short_reference_data_path, mapping):
    w = SourceDataWrapper.make_wrapper(short_reference_data_path, mapping=mapping)
    assert isinstance(w, HDF5DataWrapper)


@pytest.mark.parametrize(('from_idx', 'to_idx', 'n_rows'), ((0, None, 100), (0, 63, 63), (71, 88, 17)))
def test_creation_with_from_and_to_idx(short_reference_data_path, mapping, from_idx, to_idx, n_rows):
    w = HDF5DataWrapper(short_reference_data_path, mapping=mapping, from_idx=from_idx, to_idx=to_idx)
    assert w.n_rows == n_rows


@pytest.mark.parametrize(('start', 'stop'), ((0, 20), (25, 30), (11, 12)))
def test_load_chunk_alternative_mapping(short_reference_data_path, start, stop):
    w = HDF5DataWrapper(
        short_reference_data_path,
        mapping={'time': '/contents/time', 'rpm': '/contents/rpm', 'rad': '/contents/image0'}
    )

    chunk = w.load_chunk(start, stop)

    assert chunk.size == stop - start
    assert chunk.dtype.names == ('time', 'rpm', 'rad')
    assert chunk.dtype == w.dtype

    with h5py.File(short_reference_data_path, 'r') as data:
        assert (chunk['time'] == data['/contents/time'][start:stop]).all()
        assert (chunk['rpm'] == data['/contents/rpm'][start:stop]).all()
        assert (chunk['rad'] == data['/contents/image0'][start:stop]).all()


@pytest.mark.parametrize(("from_idx", "to_idx"), ((0, 12), (90, None)))
def test_getitem(short_reference_data_path, mapping, from_idx, to_idx):
    w = HDF5DataWrapper(short_reference_data_path, mapping=mapping, from_idx=from_idx, to_idx=to_idx)

    with h5py.File(short_reference_data_path, 'r') as data:
        for key in ('time', 'rpm', 'rad', 'amp'):
            assert isinstance(w[key], np.ndarray)
            assert (w[key] == data[mapping[key]][from_idx:to_idx]).all()
