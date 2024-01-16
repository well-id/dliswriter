import pytest
from pathlib import Path
import os
from typing import Generator
from dlisio import dlis
import numpy as np

from dlis_writer.file.file import DLISFile

from tests.common import load_dlis
from tests.dlis_files_for_testing.double_frame_dlis import write_double_frame_dlis


@pytest.fixture(scope='session')
def double_frame_data() -> tuple[dict, dict]:
    n_rows_1 = 100
    n_rows_2 = 200

    frame1_data = {
        'DEPTH': np.arange(n_rows_1),
        'RPM': 10 * np.random.rand(n_rows_1),
        'AMPLITUDE': np.random.rand(n_rows_1, 10),
    }

    frame2_data = {
        'DEPTH': np.arange(n_rows_2) / 10,
        'RPM': (np.arange(n_rows_2) % 10).astype(np.int32),
        'AMPLITUDE': np.arange(n_rows_2 * 5).reshape(n_rows_2, 5) % 6
    }

    return frame1_data, frame2_data


@pytest.fixture(scope='session')
def double_frame_dlis_path(base_data_path: Path) -> Generator:
    p = base_data_path/'double_frame.DLIS'
    yield p

    if p.exists():
        os.remove(p)


@pytest.fixture(scope='session')
def double_frame_dlis(double_frame_dlis_path: Path, double_frame_data: tuple[dict, dict]) -> Generator:
    df = write_double_frame_dlis(double_frame_dlis_path, *double_frame_data)
    yield df


@pytest.fixture(scope='session')
def double_frame_dlis_contents(double_frame_dlis_path: Path, double_frame_dlis: DLISFile) -> dlis.LogicalFile:
    with load_dlis(double_frame_dlis_path) as f:
        yield f


@pytest.fixture(scope='session')
def channels(double_frame_dlis_contents: dlis.LogicalFile) -> list[dlis.Channel]:
    return double_frame_dlis_contents.channels


def test_channel_names(channels: list[dlis.Channel]) -> None:
    assert len(channels) == 6

    names = [c.name for c in channels]
    assert names.count('DEPTH') == 2
    assert names.count('RPM') == 2
    assert names.count('AMPLITUDE') == 2


def test_channel_copy_numbers(channels: list[dlis.Channel]) -> None:
    cn = [c.copynumber for c in channels]
    assert cn.count(0) == 3
    assert cn.count(1) == 3


@pytest.mark.parametrize('nr', (0, 1))
def test_frame_channels(double_frame_dlis_contents: dlis.LogicalFile, nr: int) -> None:
    frame = double_frame_dlis_contents.frames[nr]
    assert frame.copynumber == 0  # frames have different names, so can have the same copy number

    ch = frame.channels
    assert len(ch) == 3

    assert ch[0].name == 'DEPTH'
    assert ch[1].name == 'RPM'
    assert ch[2].name == 'AMPLITUDE'

    for ch in ch:
        assert ch.copynumber == nr


@pytest.mark.parametrize('nr', (0, 1))
def test_frame_data(double_frame_dlis_contents: dlis.LogicalFile, double_frame_data: tuple[dict, dict],
                    nr: int) -> None:

    frame_channels = double_frame_dlis_contents.frames[nr].channels
    data = double_frame_data[nr]

    assert (frame_channels[0].curves() == data['DEPTH']).all()
    assert (frame_channels[1].curves() == data['RPM']).all()
    assert (frame_channels[2].curves() == data['AMPLITUDE']).all()


def test_dataset_names(double_frame_dlis: DLISFile) -> None:
    file_channels = double_frame_dlis.channels

    assert file_channels[0].dataset_name == 'DEPTH'
    assert file_channels[1].dataset_name == 'RPM'
    assert file_channels[2].dataset_name == 'AMPLITUDE'

    assert file_channels[3].dataset_name == 'DEPTH__1'
    assert file_channels[4].dataset_name == 'RPM__1'
    assert file_channels[5].dataset_name == 'AMPLITUDE__1'

    assert all(dn in double_frame_dlis._data_dict for dn in (
        'DEPTH', 'RPM', 'AMPLITUDE', 'DEPTH__1', 'RPM__1', 'AMPLITUDE__1'
    ))


@pytest.mark.parametrize(("channel_name", "dataset_name"), (("DEPTH", "depth"), ("XYZ", "XZY")))
def test_unique_dataset_name_from_dataset_name(
        double_frame_dlis: DLISFile, channel_name: str, dataset_name: str) -> None:

    ch = double_frame_dlis.add_channel(channel_name, dataset_name=dataset_name)
    assert ch.dataset_name == dataset_name


@pytest.mark.parametrize(("channel_name", "dataset_name"), (("RPM", "RPM"), ("new_channel", "AMPLITUDE")))
def test_unique_dataset_name_but_dataset_name_exists(
        double_frame_dlis: DLISFile, channel_name: str, dataset_name: str) -> None:

    with pytest.raises(ValueError, match=f"A data set with name '{dataset_name}' already exists"):
        double_frame_dlis.add_channel(channel_name, dataset_name=dataset_name)


@pytest.mark.parametrize("channel_name", ("NEW_CHANNEL", "XXX"))
def test_unique_dataset_name_from_new_channel_name(double_frame_dlis: DLISFile, channel_name: str) -> None:

    ch = double_frame_dlis.add_channel(channel_name)
    assert ch.dataset_name == channel_name


@pytest.mark.parametrize("channel_name", ("ABC", "SURFACE_RPM"))
def test_unique_dataset_name_from_repeated_channel_name(double_frame_dlis: DLISFile, channel_name: str) -> None:
    chs = []
    for i in range(5):
        chs.append(double_frame_dlis.add_channel(channel_name))

    assert chs[0].name == channel_name
    assert chs[0].dataset_name == channel_name

    for i in range(1, 5):
        assert chs[i].name == channel_name
        assert chs[i].dataset_name == f"{channel_name}__{i}"

    assert len(set(chs)) == 5  # 5 separate objects


def test_multiple_axes(double_frame_dlis_contents: dlis.LogicalFile) -> None:
    frames = double_frame_dlis_contents.frames
    for i in range(2):
        axes = frames[i].channels[0].axis
        assert len(axes) == 1
        axis = axes[0]
        assert axis.name == 'AXIS'
        assert axis.copynumber == i

    assert frames[0].channels[0].axis[0] is not frames[1].channels[0].axis[0]  # separate objects
