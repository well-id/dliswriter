import numpy as np
import pytest

from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.converters import ReprCodeConverter


def _check_conversion(arr: np.ndarray, rc: RepresentationCode) -> None:
    encoded = arr.byteswap().tobytes()
    decoded_arr = np.array(rc.decode_bytes(encoded), dtype=arr.dtype)

    assert arr.size == decoded_arr.size
    assert (arr == decoded_arr).all()
    assert arr.dtype == ReprCodeConverter.determine_numpy_dtype_from_repr_code(rc)


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
