import pytest
import numpy as np

from dlis_writer.logical_record import eflr_types
from dlis_writer.utils.source_data_wrappers import NumpyDataWrapper


@pytest.fixture
def channel1():
    return eflr_types.ChannelItem("Channel 1")


@pytest.fixture
def channel2():
    return eflr_types.ChannelItem("Channel 2")


@pytest.fixture
def channel3():
    return eflr_types.ChannelItem("Channel 3")


@pytest.fixture
def chan():
    """Mock ChannelObject instance for tests."""

    yield eflr_types.ChannelItem("some_channel")


@pytest.fixture
def channels(channel1, channel2, channel3, chan):
    return {
        'Channel 1': channel1,
        'Channel 2': channel2,
        'Channel 3': channel3,
        'some_channel': chan
    }


@pytest.fixture
def mock_data() -> NumpyDataWrapper:
    """Mock data (structured numpy array) for tests."""

    dt = np.dtype([('time', float), ('amplitude', float, (10,)), ('radius', float, (12,))])
    return NumpyDataWrapper(np.zeros(30, dtype=dt))


@pytest.fixture
def ccoef1():
    return eflr_types.CalibrationCoefficientItem("COEF-1")


@pytest.fixture
def cmeasure1():
    return eflr_types.CalibrationMeasurementItem("CMEASURE-1")


@pytest.fixture
def axis1():
    return eflr_types.AxisItem("Axis-1")


@pytest.fixture
def param1():
    return eflr_types.ParameterItem("Param-1")


@pytest.fixture
def param2():
    return eflr_types.ParameterItem("Param-2")


@pytest.fixture
def param3():
    return eflr_types.ParameterItem("Param-3")


@pytest.fixture
def zone1():
    return eflr_types.ZoneItem("Zone-1")


@pytest.fixture
def zone2():
    return eflr_types.ZoneItem("Zone-2")


@pytest.fixture
def zone3():
    return eflr_types.ZoneItem("Zone-3")


@pytest.fixture
def zones(zone1, zone2, zone3):
    return {"Zone-1": zone1, "Zone-2": zone2, "Zone-3": zone3}


@pytest.fixture
def process1():
    return eflr_types.ProcessItem("Process 1")


@pytest.fixture
def process2():
    return eflr_types.ProcessItem("Prc2")


@pytest.fixture
def channel_group(channel1, channel2, channel3):
    return eflr_types.GroupItem("Group of channels", object_type="CHANNEL",
                                object_list=[channel1, channel2, channel3])


@pytest.fixture
def process_group(process2, process1):
    return eflr_types.GroupItem("Group of processes", object_type="PROCESS", object_list=[process1, process2])


@pytest.fixture
def computation1():
    return eflr_types.ComputationItem("Compt1")


@pytest.fixture
def computation2():
    return eflr_types.ComputationItem("CMPT-2")



