import pytest
from _pytest.logging import LogCaptureFixture
from typing import Union, Any
import numpy as np
from datetime import datetime

from dlis_writer.logical_record.eflr_types.channel import ChannelSet, ChannelItem
from dlis_writer.logical_record.eflr_types.axis import AxisItem
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.utils.types import numpy_dtype_type
from dlis_writer.utils.source_data_wrappers import NumpyDataWrapper


def test_channel_creation(axis1: AxisItem) -> None:
    """Check that a ChannelObject is correctly set up."""

    channel = ChannelItem(
        'Channel',
        dataset_name='amplitude',
        long_name='Amplitude channel',
        properties=["NORMALIZED", "spliced", "local computation", "over_sampled"],
        cast_dtype=np.float32,
        units='acre',
        dimension=12,
        element_limit=12,
        source='some source',
        minimum_value=[0.],
        maximum_value=[127.6],
        axis=[axis1],
        parent=ChannelSet()
    )

    assert channel.name == 'Channel'
    assert channel.dataset_name == 'amplitude'
    assert channel.long_name.value == 'Amplitude channel'
    assert channel.properties.value == ["NORMALIZED", "SPLICED", "LOCAL-COMPUTATION", "OVER-SAMPLED"]
    assert channel.representation_code.value is RepresentationCode.FSINGL
    assert channel.units.value == 'acre'
    assert channel.dimension.value == [12]
    assert isinstance(channel.axis.value, list)
    assert isinstance(channel.axis.value[0], AxisItem)
    assert channel.axis.value[0].name == 'Axis-1'
    assert channel.element_limit.value == [12]
    assert channel.source.value == 'some source'
    assert channel.minimum_value.value == [0.]
    assert isinstance(channel.minimum_value.value[0], float)
    assert channel.maximum_value.value == [127.6]

    assert isinstance(channel.parent, ChannelSet)


@pytest.mark.parametrize("name", ("Channel-1", "amplitude"))
def test_dataset_name_not_specified(name: str) -> None:
    """Check that if dataset name is not specified, it's the same as channel name."""

    c = ChannelItem(name, parent=ChannelSet())
    assert c.name == name
    assert c.dataset_name == name


@pytest.mark.parametrize(('dimension', 'element_limit'), (([10], None), ([10, 10], None), (None, [1, 2, 3])))
def test_dimension_and_element_limit(dimension: Union[list[int], None], element_limit: Union[list[int], None]) -> None:
    """Test that it is enough to specify dimension OR element limit in the config for both to be set to that value."""

    config: dict[str, Any] = {'name': 'some channel'}

    if dimension is not None:
        config["dimension"] = dimension

    if element_limit is not None:
        config["element_limit"] = element_limit

    channel = ChannelItem(**config, parent=ChannelSet())
    channel.origin_reference = 1
    channel.make_item_body_bytes()  # defaults are set here
    assert channel.dimension.value == channel.element_limit.value
    assert channel.dimension.value is not None
    assert channel.element_limit.value is not None


def test_dimension_and_element_limit_not_specified() -> None:
    """Test that if neither dimension nor element limit are specified, none of them is set."""

    channel = ChannelItem("some channel", parent=ChannelSet())
    assert channel.dimension.value is None
    assert channel.element_limit.value is None


def test_dimension_and_element_limit_mismatch(caplog: LogCaptureFixture) -> None:
    """Test that if dimension and element limit do not match, this fact is included as a warning in log messages."""

    ch = ChannelItem('some channel', dimension=12, element_limit=(12, 10), parent=ChannelSet())
    ch.origin_reference = 1
    ch.make_item_body_bytes()  # check for the dimension and element limit mismatch is done here
    assert "For channel 'some channel', dimension is [12] and element limit is [12, 10]" in caplog.text


@pytest.mark.parametrize(("val", "unit"), (("s", 's'), ("T", 'T')))
def test_setting_unit(chan: ChannelItem, val: str, unit: str) -> None:
    """Test setting Attribute 'units' of Channel."""

    chan.units.value = val
    assert chan.units.value is unit


def test_clearing_unit(chan: ChannelItem) -> None:
    """Test removing previously defined channel unit."""

    chan.units.value = None
    assert chan.units.value is None


@pytest.mark.parametrize(("dt", "repc"), (
        (np.float64, RepresentationCode.FDOUBL),
        (np.dtype(np.float64), RepresentationCode.FDOUBL),
        (np.uint8, RepresentationCode.USHORT),
        (np.int16, RepresentationCode.SNORM),
        (np.dtype(np.int32), RepresentationCode.SLONG)
))
def test_setting_cast_dtype(chan: ChannelItem, dt: numpy_dtype_type, repc: RepresentationCode) -> None:
    """Test that representation code is correctly set based on provided cast dtype."""

    chan.cast_dtype = dt
    assert chan.representation_code.value is repc


def test_clearing_cast_dtype(chan: ChannelItem) -> None:
    """Test that clearing cast dtype also clears representation code."""

    chan.cast_dtype = np.float64
    assert chan.cast_dtype == np.float64
    assert chan.representation_code.value is not None

    chan.cast_dtype = None
    assert chan.cast_dtype is None
    assert chan.representation_code.value is None


@pytest.mark.parametrize('dt', (np.float16, np.int64, np.bool_))
def test_setting_cast_dtype_dtype_not_supported(chan: ChannelItem, dt: numpy_dtype_type) -> None:
    with pytest.raises(ValueError, match="Dtype .* is not supported.*"):
        chan.cast_dtype = dt


@pytest.mark.parametrize('dt', (float, bool, object, 4.2, datetime.now()))
def test_setting_cast_dtype_not_a_np_dtype(chan: ChannelItem, dt: Any) -> None:
    with pytest.raises(ValueError, match=".* is not a numpy dtype"):
        chan.cast_dtype = dt


@pytest.mark.parametrize('rc', (7, 'FSINGL', RepresentationCode.USHORT))
def test_setting_repr_code_error(chan: ChannelItem, rc: Any) -> None:
    with pytest.raises(RuntimeError, match="Representation code of channel should not be set directly.*"):
        chan.representation_code.value = rc


@pytest.mark.parametrize(('data', 'rc'), (
    (np.arange(10).astype(np.int32), RepresentationCode.SLONG),
    (np.random.rand(3).astype(np.float64), RepresentationCode.FDOUBL),
    (np.zeros(2).astype(np.uint16), RepresentationCode.UNORM)
))
def test_setting_repr_code_from_data(chan: ChannelItem, data: np.ndarray, rc: RepresentationCode) -> None:
    chan.cast_dtype = None

    chan._set_repr_code_from_data(data)
    assert chan.cast_dtype == data.dtype
    assert chan.representation_code.value is rc


@pytest.mark.parametrize(('dt', 'data', 'rc'), (
    (np.int8, np.arange(10).astype(np.int16), RepresentationCode.SSHORT),
    (np.float32, np.random.rand(3).astype(np.float64), RepresentationCode.FSINGL),
    (np.int16, np.zeros(2).astype(np.uint16), RepresentationCode.SNORM),
    (np.uint16, np.zeros(2).astype(np.int16), RepresentationCode.UNORM)
))
def test_setting_repr_code_from_data_mismatch(chan: ChannelItem, dt: numpy_dtype_type, data: np.ndarray,
                                              rc: RepresentationCode, caplog: pytest.LogCaptureFixture) -> None:
    chan.cast_dtype = dt
    assert chan.cast_dtype == dt
    assert chan.representation_code.value is rc

    chan._set_repr_code_from_data(data)

    assert f"Data will be cast from {data.dtype} to {dt}" in caplog.text

    # not changed!
    assert chan.cast_dtype != data.dtype
    assert chan.cast_dtype == dt
    assert chan.representation_code.value is rc


def test_attribute_set_directly_error(chan: ChannelItem) -> None:
    """Test that a RuntimeError is raised if an attempt to set an Attribute directly is made."""

    with pytest.raises(RuntimeError, match="Cannot set DLIS Attribute 'units'.*"):
        chan.units = 'm'    # type: ignore  # mypy property setter bug

    with pytest.raises(RuntimeError, match="Cannot set DLIS Attribute 'long_name'.*"):
        chan.long_name = 'Lorem ipsum'    # type: ignore  # mypy property setter bug


@pytest.mark.parametrize('value', (10.6, [10, 11.2]))
def test_setting_dimension_error(chan: ChannelItem, value: Any) -> None:
    """Test that a ValueError is raised if an un-parsable value is attempted to be set as dimension."""

    with pytest.raises(ValueError):
        chan.dimension.value = value


@pytest.mark.parametrize(("name", "dim"), (("time", [1]), ("amplitude", [10]), ('radius', [12])))
def test_setting_dimension_from_data(chan: ChannelItem, mock_data: NumpyDataWrapper, name: str, dim: list[int]) -> None:
    """Check that dimension and element limit are correctly inferred from data."""

    chan.name = name
    chan.set_dimension_and_repr_code_from_data(mock_data)
    assert chan.dimension.value == dim
    assert chan.element_limit.value == dim


@pytest.mark.parametrize(("name", "dim", "prev_dim"), (("time", [1], [30]), ("amplitude", [10], [1])))
def test_setting_dimension_from_data_mismatched_dimension(chan: ChannelItem, mock_data: NumpyDataWrapper, name: str,
                                                          dim: list[int], prev_dim: list[int],
                                                          caplog: LogCaptureFixture) -> None:
    """Test that if dimension from data does not match the previously set one, a warning is included in logs."""

    chan.name = name
    chan.dimension.value = prev_dim
    chan.set_dimension_and_repr_code_from_data(mock_data)
    assert chan.dimension.value == dim
    assert "Previously defined dimension" in caplog.text


@pytest.mark.parametrize(("name", "dim", "prev_dim"), (("time", [1], [0]), ("radius", [12], [10])))
def test_setting_dimension_from_data_mismatched_element_limit(chan: ChannelItem, mock_data: NumpyDataWrapper, name: str,
                                                              dim: list[int], prev_dim: list[int],
                                                              caplog: LogCaptureFixture) -> None:
    """Test that if element limit from data does not match the previously set one, a warning is included in logs."""

    chan.name = name
    chan.element_limit.value = prev_dim
    chan.set_dimension_and_repr_code_from_data(mock_data)
    assert chan.element_limit.value == dim
    assert "Previously defined element limit" in caplog.text


def test_copy_numbers(chan: ChannelItem) -> None:
    ch1 = ChannelItem('X', chan.parent)
    ch2 = ChannelItem('X', chan.parent)
    ch3 = ChannelItem('X', chan.parent)

    assert ch1.copy_number == 0
    assert ch2.copy_number == 1
    assert ch3.copy_number == 2

    assert chan.copy_number == 0
    chan_chan = ChannelItem(chan.name, parent=chan.parent)
    assert chan_chan.copy_number == 1
