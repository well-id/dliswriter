import pytest
import numpy as np
from pathlib import Path
import h5py    # type: ignore  # untyped library
import os

from dlis_writer.logical_record import eflr_types
from dlis_writer.utils.source_data_wrappers import NumpyDataWrapper

from tests.common import clear_eflr_instance_registers, load_dlis
from tests.dlis_files_for_testing import write_short_dlis


@pytest.fixture(autouse=True)
def cleanup():
    """Remove all defined EFLR instances from the internal dicts before each test."""

    clear_eflr_instance_registers()
    yield


@pytest.fixture(scope='session')
def base_data_path() -> Path:
    """Path to the resources files."""

    return Path(__file__).resolve().parent


@pytest.fixture(scope='session')
def reference_data_path(base_data_path: Path) -> Path:
    """Path to the reference HDF5 data file."""

    return base_data_path / 'resources/mock_data.hdf5'


@pytest.fixture(scope='session')
def reference_data(reference_data_path: Path):
    """The reference HDF5 data file, open in read mode."""

    f = h5py.File(reference_data_path, 'r')
    yield f
    f.close()


@pytest.fixture(scope='session')
def short_reference_data_path(base_data_path: Path) -> Path:
    """Path to the HDF5 file with short version of the reference data."""

    return base_data_path / 'resources/mock_data_short.hdf5'


@pytest.fixture(scope='session')
def short_reference_data(short_reference_data_path: Path):
    """The reference short HDF5 data file, open in read mode."""

    f = h5py.File(short_reference_data_path, 'r')
    yield f
    f.close()


@pytest.fixture(scope='session')
def short_dlis(short_reference_data_path: Path, base_data_path: Path):
    """A freshly written DLIS file - used in tests to check if all contents are there as expected."""

    clear_eflr_instance_registers()

    dlis_path = base_data_path / 'outputs/new_fake_dlis_shared.DLIS'
    write_short_dlis(dlis_path, data=short_reference_data_path)

    with load_dlis(dlis_path) as f:
        yield f

    if dlis_path.exists():  # does not exist if file creation failed
        os.remove(dlis_path)


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
