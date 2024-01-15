import numpy as np
import pytest
from typing import Any
from datetime import datetime, timedelta
from enum import Enum
from struct import Struct

from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.converters import ReprCodeConverter, numpy_dtype_type


@pytest.mark.parametrize(('dt', 'rc'), (
        (np.float64, RepresentationCode.FDOUBL),
        (np.float32, RepresentationCode.FSINGL),
        (np.int32, RepresentationCode.SLONG),
        (np.int16, RepresentationCode.SNORM),
        (np.int8, RepresentationCode.SSHORT),
        (np.uint32, RepresentationCode.ULONG),
        (np.uint16, RepresentationCode.UNORM),
        (np.uint8, RepresentationCode.USHORT),
))
def test_determine_repr_code_from_numpy_dtype(dt: numpy_dtype_type, rc: RepresentationCode) -> None:
    assert ReprCodeConverter.determine_repr_code_from_numpy_dtype(dt) is rc
    assert ReprCodeConverter.determine_repr_code_from_numpy_dtype(np.dtype(dt)) is rc


@pytest.mark.parametrize(('t', 'rc'), (
        (int, RepresentationCode.SLONG),
        (float, RepresentationCode.FDOUBL),
        (str, RepresentationCode.ASCII),
        (datetime, RepresentationCode.DTIME)
))
def test_determine_repr_code_from_generic_type(t: type, rc: RepresentationCode) -> None:
    assert ReprCodeConverter.determine_repr_code_from_generic_type(t) is rc


@pytest.mark.parametrize('t', (object, Enum, np.ndarray, Struct, dict, set, list, tuple))
def test_cannot_determine_repr_code_from_type(t: type) -> None:
    with pytest.raises(ReprCodeConverter.ReprCodeError, match="Cannot determine representation code for type.*"):
        ReprCodeConverter.determine_repr_code_from_generic_type(t)


@pytest.mark.parametrize('t', (1, 123.1, [1, 2, 4], 'abc'))
def test_determine_repr_code_from_generic_type_not_a_type(t: Any) -> None:
    with pytest.raises(TypeError, match=".* is not a type"):
        ReprCodeConverter.determine_repr_code_from_generic_type(t)


@pytest.mark.parametrize(('v', 'rc'), (
        (datetime.now(), RepresentationCode.DTIME),
        (2, RepresentationCode.SLONG),
        (-10208329, RepresentationCode.SLONG),
        (-92003198.2, RepresentationCode.FDOUBL),
        (3.123121231, RepresentationCode.FDOUBL),
        ('abc', RepresentationCode.ASCII),
        (np.arange(10), RepresentationCode.SLONG),
        (np.random.rand(12, 13), RepresentationCode.FDOUBL)
))
def test_determine_repr_code_from_value_single(v: Any, rc: RepresentationCode) -> None:
    assert ReprCodeConverter.determine_repr_code_from_value(v) is rc


@pytest.mark.parametrize(('v', 'rc'), (
        ([1, 2, 3], RepresentationCode.SLONG),
        ((1, 2, 3.5), RepresentationCode.FDOUBL),
        ('abcd', RepresentationCode.ASCII),
        (['a', 'b', 'c'], RepresentationCode.ASCII),
        ([datetime.now(), datetime.now() + timedelta(seconds=5)], RepresentationCode.DTIME)
))
def test_determine_repr_code_from_value_multiple(v: Any, rc: RepresentationCode) -> None:
    assert ReprCodeConverter.determine_repr_code_from_value(v) is rc


@pytest.mark.parametrize('v', (
    [0, 1, datetime.now()],
    [1, '1'],
    ('0.1', 0.2, '0.3')
))
def test_cannot_determine_common_repr_code(v: Any) -> None:
    with pytest.raises(ReprCodeConverter.ReprCodeError, match="Cannot determine a common representation code"):
        ReprCodeConverter.determine_repr_code_from_value(v)


@pytest.mark.parametrize(('rc', 'dt'), (
        (RepresentationCode.FDOUBL, np.float64),
        (RepresentationCode.FSINGL, np.float32),
        (RepresentationCode.SLONG, np.int32),
        (RepresentationCode.SNORM, np.int16),
        (RepresentationCode.SSHORT, np.int8),
        (RepresentationCode.ULONG, np.uint32),
        (RepresentationCode.UNORM, np.uint16),
        (RepresentationCode.USHORT, np.uint8)
))
def test_determine_numpy_dtype_from_repr_code(rc: RepresentationCode, dt: type[np.generic]) -> None:
    assert ReprCodeConverter.determine_numpy_dtype_from_repr_code(rc) == dt
