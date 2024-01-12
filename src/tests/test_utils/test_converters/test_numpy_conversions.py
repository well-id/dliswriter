import numpy as np
import pytest
from pathlib import Path

from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.converters import ReprCodeConverter

from tests.dlis_files_for_testing.dict_based_dlis import write_dict_based_dlis
from tests.common import load_dlis, select_channel


def _check_conversion(arr: np.ndarray, rc: RepresentationCode) -> None:
    encoded = arr.byteswap().tobytes()
    decoded_arr = np.array(rc.decode_bytes(encoded), dtype=arr.dtype)

    assert arr.size == decoded_arr.size
    assert (arr == decoded_arr).all()
    assert arr.dtype == ReprCodeConverter.get_dtype(rc)


@pytest.mark.parametrize("data", (
        np.arange(10).astype(np.float64),
        np.array([0], dtype=np.float64),
        np.random.rand(100),
        10 * np.random.rand(20) - 5
))
def test_floats(data):
    _check_conversion(data.astype(np.float64), RepresentationCode.FDOUBL)
    _check_conversion(data.astype(np.float32), RepresentationCode.FSINGL)


@pytest.mark.parametrize("data", (
        np.arange(10),
        np.arange(100) - 20,
        np.array([-528]),
        np.array([20, 21, 20, 2311, -1000]),
        np.random.randint(low=-20, high=412, size=100)
))
def test_signed_ints(data):
    _check_conversion(data.astype(np.int32), RepresentationCode.SLONG)
    _check_conversion(data.astype(np.int16), RepresentationCode.SNORM)
    _check_conversion(data.astype(np.int8), RepresentationCode.SSHORT)


@pytest.mark.parametrize("data", (
        np.arange(100),
        np.array([0, 20, 21, 20, 2311]),
        np.random.randint(low=0, high=1412, size=100)
))
def test_unsigned_ints(data):
    _check_conversion(data.astype(np.uint32), RepresentationCode.ULONG)
    _check_conversion(data.astype(np.uint16), RepresentationCode.UNORM)
    _check_conversion(data.astype(np.uint8), RepresentationCode.USHORT)


@pytest.mark.parametrize('data_arr', (
    np.random.rand(100).astype(np.float64),
    np.random.rand(10, 20).astype(np.float64),
    np.random.rand(30, 10).astype(np.float32),
    np.random.randint(0, 2**8, size=15, dtype=np.uint8),
    np.random.randint(-2**16, 2**16-1, size=280, dtype=np.int32),
    np.random.randint(-2**15, 2**15-1, size=33, dtype=np.int16),
    np.random.randint(-2**7, 2**7-1, size=(12, 13), dtype=np.int8)
))
def test_all_types(new_dlis_path: Path, data_arr: np.ndarray):

    data_arr = np.atleast_2d(data_arr)
    data_dict = {
        'index': np.arange(data_arr.shape[0]).astype(np.float64),
        'data': data_arr
    }

    write_dict_based_dlis(new_dlis_path, data_dict=data_dict)

    with load_dlis(new_dlis_path) as f:
        ch = select_channel(f, 'data')
        assert ch.dimension == [data_arr.shape[-1]]
        assert (ch.curves() == data_arr).all()


