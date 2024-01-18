import pytest
import numpy as np
from pathlib import Path
import h5py    # type: ignore  # untyped library
import os
from typing import Generator

from dlis_writer.logical_record import eflr_types
from dlis_writer.utils.source_data_wrappers import NumpyDataWrapper

from tests.common import load_dlis
from tests.dlis_files_for_testing import write_short_dlis


@pytest.fixture(scope='session')
def base_data_path() -> Path:
    """Path to the resources files."""

    return Path(__file__).resolve().parent


@pytest.fixture(scope='session')
def reference_data_path(base_data_path: Path) -> Path:
    """Path to the reference HDF5 data file."""

    return base_data_path / 'resources/mock_data.hdf5'


@pytest.fixture(scope='session')
def reference_data(reference_data_path: Path) -> Generator:
    """The reference HDF5 data file, open in read mode."""

    f = h5py.File(reference_data_path, 'r')
    yield f
    f.close()


@pytest.fixture(scope='session')
def short_reference_data_path(base_data_path: Path) -> Path:
    """Path to the HDF5 file with short version of the reference data."""

    return base_data_path / 'resources/mock_data_short.hdf5'


@pytest.fixture(scope='session')
def short_reference_data(short_reference_data_path: Path) -> Generator:
    """The reference short HDF5 data file, open in read mode."""

    f = h5py.File(short_reference_data_path, 'r')
    yield f
    f.close()


@pytest.fixture(scope='session')
def short_dlis(short_reference_data_path: Path, base_data_path: Path) -> Generator:
    """A freshly written DLIS file - used in tests to check if all contents are there as expected."""

    dlis_path = base_data_path / 'outputs/new_fake_dlis_shared.DLIS'
    write_short_dlis(dlis_path, data=short_reference_data_path)

    with load_dlis(dlis_path) as f:
        yield f

    if dlis_path.exists():  # does not exist if file creation failed
        os.remove(dlis_path)


@pytest.fixture
def new_dlis_path(base_data_path: Path) -> Generator:
    """Path for a new DLIS file to be created. The file is removed afterwards."""

    new_path = base_data_path/'outputs/new_fake_dlis.DLIS'
    os.makedirs(new_path.parent, exist_ok=True)
    yield new_path

    if new_path.exists():  # does not exist if file creation failed
        os.remove(new_path)


@pytest.fixture
def channel_parent() -> eflr_types.ChannelSet:
    return eflr_types.ChannelItem.make_parent()


@pytest.fixture
def channel1(channel_parent: eflr_types.ChannelSet) -> eflr_types.ChannelItem:
    return eflr_types.ChannelItem("Channel 1", parent=channel_parent)


@pytest.fixture
def channel2(channel_parent: eflr_types.ChannelSet) -> eflr_types.ChannelItem:
    return eflr_types.ChannelItem("Channel 2", parent=channel_parent)


@pytest.fixture
def channel3(channel_parent: eflr_types.ChannelSet) -> eflr_types.ChannelItem:
    return eflr_types.ChannelItem("Channel 3", parent=channel_parent)


@pytest.fixture
def chan(channel_parent: eflr_types.ChannelSet) -> Generator:
    """Mock ChannelItem instance for tests."""

    yield eflr_types.ChannelItem("some_channel", parent=channel_parent)


@pytest.fixture
def channels(channel1: eflr_types.ChannelItem, channel2: eflr_types.ChannelItem, channel3: eflr_types.ChannelItem,
             chan: eflr_types.ChannelItem) -> dict:
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
def ccoef1() -> eflr_types.CalibrationCoefficientItem:
    return eflr_types.CalibrationCoefficientItem("COEF-1", parent=eflr_types.CalibrationCoefficientSet())


@pytest.fixture
def cmeasure1() -> eflr_types.CalibrationMeasurementItem:
    return eflr_types.CalibrationMeasurementItem("CMEASURE-1", parent=eflr_types.CalibrationMeasurementSet())


@pytest.fixture
def axis1() -> eflr_types.AxisItem:
    return eflr_types.AxisItem("Axis-1", parent=eflr_types.AxisItem.make_parent())


@pytest.fixture
def param_parent() -> eflr_types.ParameterSet:
    return eflr_types.ParameterItem.make_parent()


@pytest.fixture
def param1(param_parent: eflr_types.ParameterSet) -> eflr_types.ParameterItem:
    return eflr_types.ParameterItem("Param-1", parent=param_parent)


@pytest.fixture
def param2(param_parent: eflr_types.ParameterSet) -> eflr_types.ParameterItem:
    return eflr_types.ParameterItem("Param-2", parent=param_parent)


@pytest.fixture
def param3(param_parent: eflr_types.ParameterSet) -> eflr_types.ParameterItem:
    return eflr_types.ParameterItem("Param-3", parent=param_parent)


@pytest.fixture
def zone_parent() -> eflr_types.ZoneSet:
    return eflr_types.ZoneItem.make_parent()


@pytest.fixture
def zone1(zone_parent: eflr_types.ZoneSet) -> eflr_types.ZoneItem:
    return eflr_types.ZoneItem("Zone-1", parent=zone_parent)


@pytest.fixture
def zone2(zone_parent: eflr_types.ZoneSet) -> eflr_types.ZoneItem:
    return eflr_types.ZoneItem("Zone-2", parent=zone_parent)


@pytest.fixture
def zone3(zone_parent: eflr_types.ZoneSet) -> eflr_types.ZoneItem:
    return eflr_types.ZoneItem("Zone-3", parent=zone_parent)


@pytest.fixture
def zones(zone1: eflr_types.ZoneItem, zone2: eflr_types.ZoneItem, zone3: eflr_types.ZoneItem) -> dict:
    return {"Zone-1": zone1, "Zone-2": zone2, "Zone-3": zone3}


@pytest.fixture
def process_parent() -> eflr_types.ProcessSet:
    return eflr_types.ProcessSet()


@pytest.fixture
def process1(process_parent: eflr_types.ProcessSet) -> eflr_types.ProcessItem:
    return eflr_types.ProcessItem("Process 1", parent=process_parent)


@pytest.fixture
def process2(process_parent: eflr_types.ProcessSet) -> eflr_types.ProcessItem:
    return eflr_types.ProcessItem("Prc2", parent=process_parent)


@pytest.fixture
def channel_group(channel1: eflr_types.ChannelItem, channel2: eflr_types.ChannelItem,
                  channel3: eflr_types.ChannelItem) -> eflr_types.GroupItem:
    return eflr_types.GroupItem("Group of channels", object_type="CHANNEL",
                                object_list=[channel1, channel2, channel3], parent=eflr_types.GroupSet())


@pytest.fixture
def process_group(process2: eflr_types.ProcessItem, process1: eflr_types.ProcessItem) -> eflr_types.GroupItem:
    return eflr_types.GroupItem("Group of processes", object_type="PROCESS", object_list=[process1, process2],
                                parent=eflr_types.GroupSet())


@pytest.fixture
def computation1() -> eflr_types.ComputationItem:
    return eflr_types.ComputationItem("Compt1", parent=eflr_types.ComputationSet())


@pytest.fixture
def computation2() -> eflr_types.ComputationItem:
    return eflr_types.ComputationItem("CMPT-2", parent=eflr_types.ComputationItem.make_parent())
